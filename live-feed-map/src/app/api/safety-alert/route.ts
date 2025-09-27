import { NextResponse } from 'next/server';

interface SafetyAlert {
  id: string;
  type: 'automatic_alert' | 'manual_override';
  firefighterId: string;
  timestamp: string;
  inactivityTime?: number;
  overrideCount?: number;
  status: 'active' | 'resolved' | 'override';
}

interface SafetyLog {
  id: string;
  firefighterId: string;
  eventType: 'alert' | 'override' | 'reset';
  timestamp: string;
  data: any;
  userId?: string;
}

// In-memory storage for safety alerts and logs
let safetyAlerts: SafetyAlert[] = [];
let safetyLogs: SafetyLog[] = [];
const MAX_ALERTS = 100;
const MAX_LOGS = 500;

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { type, firefighterId, timestamp, inactivityTime, overrideCount } = body;

    if (!type || !firefighterId || !timestamp) {
      return NextResponse.json({ 
        success: false, 
        message: 'Missing required fields: type, firefighterId, timestamp' 
      }, { status: 400 });
    }

    const alertId = Date.now().toString();
    
    // Create safety alert
    const newAlert: SafetyAlert = {
      id: alertId,
      type,
      firefighterId,
      timestamp,
      inactivityTime,
      overrideCount,
      status: type === 'manual_override' ? 'override' : 'active'
    };

    // Add to alerts array
    safetyAlerts.unshift(newAlert);
    if (safetyAlerts.length > MAX_ALERTS) {
      safetyAlerts = safetyAlerts.slice(0, MAX_ALERTS);
    }

    // Create safety log entry
    const newLog: SafetyLog = {
      id: Date.now().toString(),
      firefighterId,
      eventType: type === 'manual_override' ? 'override' : 'alert',
      timestamp,
      data: {
        alertId,
        inactivityTime,
        overrideCount,
        type
      }
    };

    safetyLogs.unshift(newLog);
    if (safetyLogs.length > MAX_LOGS) {
      safetyLogs = safetyLogs.slice(0, MAX_LOGS);
    }

    // If it's a manual override, resolve any active alerts for this firefighter
    if (type === 'manual_override') {
      safetyAlerts = safetyAlerts.map(alert => 
        alert.firefighterId === firefighterId && alert.status === 'active'
          ? { ...alert, status: 'resolved' }
          : alert
      );
    }

    console.log('Safety alert processed:', newAlert);
    console.log('Safety log created:', newLog);

    return NextResponse.json({ 
      success: true, 
      message: 'Safety alert processed successfully',
      alert: newAlert,
      log: newLog
    }, { status: 200 });

  } catch (error) {
    console.error('Error processing safety alert:', error);
    return NextResponse.json({ 
      success: false, 
      message: 'Internal server error' 
    }, { status: 500 });
  }
}

export async function GET(request: Request) {
  try {
    const { searchParams } = new URL(request.url);
    const firefighterId = searchParams.get('firefighterId');
    const type = searchParams.get('type');
    const status = searchParams.get('status');

    let filteredAlerts = safetyAlerts;
    let filteredLogs = safetyLogs;

    // Filter alerts
    if (firefighterId) {
      filteredAlerts = filteredAlerts.filter(alert => alert.firefighterId === firefighterId);
    }
    if (type) {
      filteredAlerts = filteredAlerts.filter(alert => alert.type === type);
    }
    if (status) {
      filteredAlerts = filteredAlerts.filter(alert => alert.status === status);
    }

    // Filter logs
    if (firefighterId) {
      filteredLogs = filteredLogs.filter(log => log.firefighterId === firefighterId);
    }

    return NextResponse.json({ 
      success: true, 
      alerts: filteredAlerts,
      logs: filteredLogs,
      summary: {
        totalAlerts: safetyAlerts.length,
        activeAlerts: safetyAlerts.filter(a => a.status === 'active').length,
        totalOverrides: safetyAlerts.filter(a => a.type === 'manual_override').length,
        totalLogs: safetyLogs.length
      }
    }, { status: 200 });

  } catch (error) {
    console.error('Error fetching safety data:', error);
    return NextResponse.json({ 
      success: false, 
      message: 'Internal server error' 
    }, { status: 500 });
  }
}

export async function PUT(request: Request) {
  try {
    const body = await request.json();
    const { alertId, status, firefighterId } = body;

    if (!alertId || !status) {
      return NextResponse.json({ 
        success: false, 
        message: 'Missing required fields: alertId, status' 
      }, { status: 400 });
    }

    // Update alert status
    const alertIndex = safetyAlerts.findIndex(alert => alert.id === alertId);
    if (alertIndex === -1) {
      return NextResponse.json({ 
        success: false, 
        message: 'Alert not found' 
      }, { status: 404 });
    }

    safetyAlerts[alertIndex].status = status;

    // Create log entry for status change
    const newLog: SafetyLog = {
      id: Date.now().toString(),
      firefighterId: firefighterId || safetyAlerts[alertIndex].firefighterId,
      eventType: 'reset',
      timestamp: new Date().toISOString(),
      data: {
        alertId,
        newStatus: status,
        previousStatus: safetyAlerts[alertIndex].status
      }
    };

    safetyLogs.unshift(newLog);
    if (safetyLogs.length > MAX_LOGS) {
      safetyLogs = safetyLogs.slice(0, MAX_LOGS);
    }

    console.log('Alert status updated:', safetyAlerts[alertIndex]);
    console.log('Status change logged:', newLog);

    return NextResponse.json({ 
      success: true, 
      message: 'Alert status updated successfully',
      alert: safetyAlerts[alertIndex]
    }, { status: 200 });

  } catch (error) {
    console.error('Error updating alert status:', error);
    return NextResponse.json({ 
      success: false, 
      message: 'Internal server error' 
    }, { status: 500 });
  }
}
