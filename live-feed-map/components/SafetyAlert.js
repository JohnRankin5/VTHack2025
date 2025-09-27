'use client';

import { useState, useEffect, useRef } from 'react';

const SafetyAlert = ({ firefighterId = 'FF-001', onAlert, onOverride }) => {
  const [isActive, setIsActive] = useState(false);
  const [inactivityTimer, setInactivityTimer] = useState(0);
  const [lastActivity, setLastActivity] = useState(Date.now());
  const [alertStatus, setAlertStatus] = useState('normal'); // normal, warning, alert, override
  const [overrideCount, setOverrideCount] = useState(0);
  const [lastOverride, setLastOverride] = useState(null);
  const [isTestMode, setIsTestMode] = useState(false);
  const [testScenario, setTestScenario] = useState('normal'); // normal, passed_out, stuck
  
  const timerRef = useRef(null);
  const activitySimulationRef = useRef(null);
  const inactivityThreshold = 5000; // 5 seconds
  const warningThreshold = 3000; // 3 seconds

  // Simulate IMU activity detection
  useEffect(() => {
    // Clear any existing simulation
    if (activitySimulationRef.current) {
      clearTimeout(activitySimulationRef.current);
      activitySimulationRef.current = null;
    }

    // Don't start simulation if in "passed_out" test scenario
    if (isTestMode && testScenario === 'passed_out') {
      return;
    }

    const simulateActivity = () => {
      if (isTestMode && testScenario === 'passed_out') {
        return; // Stop all activity simulation
      }
      
      if (isTestMode && testScenario === 'stuck') {
        // In test mode with "stuck" scenario, simulate very infrequent activity
        const randomDelay = Math.random() * 8000 + 6000; // 6-14 seconds
        activitySimulationRef.current = setTimeout(() => {
          if (alertStatus !== 'override' && isTestMode && testScenario === 'stuck') {
            setLastActivity(Date.now());
            setInactivityTimer(0);
            setAlertStatus('normal');
          }
          simulateActivity();
        }, randomDelay);
        return;
      }
      
      // Normal simulation - random activity every 1-3 seconds
      const randomDelay = Math.random() * 2000 + 1000;
      activitySimulationRef.current = setTimeout(() => {
        if (alertStatus !== 'override' && !(isTestMode && testScenario === 'passed_out')) {
          setLastActivity(Date.now());
          setInactivityTimer(0);
          setAlertStatus('normal');
        }
        simulateActivity();
      }, randomDelay);
    };

    simulateActivity();

    // Cleanup function
    return () => {
      if (activitySimulationRef.current) {
        clearTimeout(activitySimulationRef.current);
        activitySimulationRef.current = null;
      }
    };
  }, [alertStatus, isTestMode, testScenario]);

  // Inactivity monitoring
  useEffect(() => {
    if (alertStatus === 'override') return;

    timerRef.current = setInterval(() => {
      const now = Date.now();
      const timeSinceActivity = now - lastActivity;
      
      setInactivityTimer(timeSinceActivity);

      if (timeSinceActivity >= inactivityThreshold) {
        setAlertStatus('alert');
        setIsActive(true);
        if (onAlert) {
          onAlert({
            type: 'automatic_alert',
            firefighterId,
            timestamp: new Date().toISOString(),
            inactivityTime: timeSinceActivity
          });
        }
      } else if (timeSinceActivity >= warningThreshold) {
        setAlertStatus('warning');
      }
    }, 100);

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current);
      }
    };
  }, [lastActivity, alertStatus, inactivityThreshold, warningThreshold, firefighterId, onAlert]);

  const handleManualCheckIn = async () => {
    const now = Date.now();
    const overrideData = {
      type: 'manual_override',
      firefighterId,
      timestamp: new Date().toISOString(),
      inactivityTime: now - lastActivity,
      overrideCount: overrideCount + 1
    };

    // Reset all timers and status
    setLastActivity(now);
    setInactivityTimer(0);
    setAlertStatus('override');
    setIsActive(false);
    setOverrideCount(prev => prev + 1);
    setLastOverride(now);

    // Log the override
    try {
      const response = await fetch('/api/safety-alert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(overrideData),
      });

      if (response.ok) {
        console.log('Manual override logged successfully');
      }
    } catch (error) {
      console.error('Error logging manual override:', error);
    }

    // Notify parent component
    if (onOverride) {
      onOverride(overrideData);
    }

    // Reset to normal after 2 seconds
    setTimeout(() => {
      setAlertStatus('normal');
    }, 2000);
  };

  const handleTestMode = () => {
    setIsTestMode(!isTestMode);
    if (!isTestMode) {
      setTestScenario('normal');
    }
  };

  const handleTestScenario = (scenario) => {
    // Clear any existing activity simulation
    if (activitySimulationRef.current) {
      clearTimeout(activitySimulationRef.current);
      activitySimulationRef.current = null;
    }

    setTestScenario(scenario);
    if (scenario === 'passed_out') {
      // Immediately stop activity simulation to trigger alert
      setLastActivity(Date.now() - 6000); // Set 6 seconds ago to trigger alert
      setInactivityTimer(6000); // Set timer to 6 seconds
    } else if (scenario === 'stuck') {
      // Set activity to 4 seconds ago to show warning
      setLastActivity(Date.now() - 4000);
      setInactivityTimer(4000); // Set timer to 4 seconds
    } else {
      // Reset to normal
      setLastActivity(Date.now());
      setInactivityTimer(0);
      setAlertStatus('normal');
    }
  };

  const getStatusColor = () => {
    switch (alertStatus) {
      case 'normal': return 'text-green-400';
      case 'warning': return 'text-yellow-400';
      case 'alert': return 'text-red-400';
      case 'override': return 'text-blue-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusText = () => {
    switch (alertStatus) {
      case 'normal': return 'ACTIVE';
      case 'warning': return 'WARNING';
      case 'alert': return 'ALERT';
      case 'override': return 'OVERRIDE';
      default: return 'UNKNOWN';
    }
  };

  const getButtonColor = () => {
    if (alertStatus === 'override') {
      return 'bg-blue-600 hover:bg-blue-700 text-white animate-pulse';
    }
    return 'bg-green-600 hover:bg-green-700 text-white';
  };

  return (
    <div className="bg-gradient-to-b from-slate-700 to-slate-800 p-4 rounded-lg border border-orange-500/30 shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${
            alertStatus === 'normal' ? 'bg-green-400' :
            alertStatus === 'warning' ? 'bg-yellow-400 animate-pulse' :
            alertStatus === 'alert' ? 'bg-red-400 animate-pulse' :
            'bg-blue-400 animate-pulse'
          }`}></div>
          <h3 className="text-sm font-bold text-orange-400 tracking-wide">SAFETY MONITOR</h3>
        </div>
        <div className={`text-xs font-bold ${getStatusColor()}`}>
          {getStatusText()}
        </div>
      </div>

      {/* Firefighter ID and Status */}
      <div className="mb-4 p-3 bg-slate-600/50 rounded-lg border border-slate-500/50">
        <div className="text-xs text-slate-300 mb-1">FIREFIGHTER ID</div>
        <div className="text-sm font-mono text-white font-bold">{firefighterId}</div>
        <div className="text-xs text-slate-400 mt-1">
          Last Activity: {Math.floor(inactivityTimer / 1000)}s ago
        </div>
      </div>

      {/* Manual Check-in Button */}
      <div className="mb-4">
        <button
          onClick={handleManualCheckIn}
          disabled={alertStatus === 'override'}
          className={`w-full py-3 px-4 rounded-lg text-sm font-bold transition-all duration-200 ${getButtonColor()} disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {alertStatus === 'override' ? '✅ CHECK-IN CONFIRMED' : '🟢 MANUAL CHECK-IN'}
        </button>
        {alertStatus === 'override' && (
          <div className="text-xs text-blue-400 text-center mt-2 font-semibold">
            Override logged - Timer reset
          </div>
        )}
      </div>

      {/* Alert Status Display */}
      {isActive && alertStatus === 'alert' && (
        <div className="mb-4 p-3 bg-red-600/20 border border-red-500/50 rounded-lg">
          <div className="text-xs text-red-300 font-bold mb-1">AUTOMATIC ALERT TRIGGERED</div>
          <div className="text-sm text-red-200">
            No movement detected for {Math.floor(inactivityTimer / 1000)} seconds
          </div>
          <div className="text-xs text-red-300 mt-1">
            Press "MANUAL CHECK-IN" if firefighter is safe
          </div>
        </div>
      )}

      {/* Override Statistics */}
      <div className="text-xs text-slate-400 space-y-1">
        <div>Manual Overrides: {overrideCount}</div>
        {lastOverride && (
          <div>Last Override: {new Date(lastOverride).toLocaleTimeString()}</div>
        )}
      </div>

      {/* Test Mode Controls */}
      <div className="mt-4 p-3 bg-slate-600/30 rounded-lg border border-slate-500/30">
        <div className="flex items-center justify-between mb-2">
          <div className="text-xs text-slate-300 font-semibold">TEST MODE</div>
          <button
            onClick={handleTestMode}
            className={`px-2 py-1 rounded text-xs font-bold transition-all ${
              isTestMode 
                ? 'bg-orange-600 hover:bg-orange-700 text-white' 
                : 'bg-slate-600 hover:bg-slate-700 text-slate-300'
            }`}
          >
            {isTestMode ? 'EXIT TEST' : 'TEST MODE'}
          </button>
        </div>
        
        {isTestMode && (
          <div className="space-y-2">
            <div className="text-xs text-slate-400 mb-2">Simulate Emergency Scenarios:</div>
            <div className="grid grid-cols-1 gap-1">
              <button
                onClick={() => handleTestScenario('normal')}
                className={`px-2 py-1 rounded text-xs font-bold transition-all ${
                  testScenario === 'normal' 
                    ? 'bg-green-600 text-white' 
                    : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
                }`}
              >
                🟢 Normal Operation
              </button>
              <button
                onClick={() => handleTestScenario('stuck')}
                className={`px-2 py-1 rounded text-xs font-bold transition-all ${
                  testScenario === 'stuck' 
                    ? 'bg-yellow-600 text-white' 
                    : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
                }`}
              >
                🟡 Firefighter Stuck (Warning)
              </button>
              <button
                onClick={() => handleTestScenario('passed_out')}
                className={`px-2 py-1 rounded text-xs font-bold transition-all ${
                  testScenario === 'passed_out' 
                    ? 'bg-red-600 text-white' 
                    : 'bg-slate-700 hover:bg-slate-600 text-slate-300'
                }`}
              >
                🔴 Firefighter Passed Out (Alert)
              </button>
            </div>
            <div className="text-xs text-slate-500 mt-2">
              {testScenario === 'normal' && 'Simulating normal movement patterns'}
              {testScenario === 'stuck' && 'Simulating infrequent movement (firefighter stuck)'}
              {testScenario === 'passed_out' && 'Simulating no movement (firefighter unconscious)'}
            </div>
          </div>
        )}
      </div>

      {/* Status Indicators */}
      <div className="flex justify-center mt-4">
        <div className={`flex items-center gap-2 px-3 py-2 rounded-lg border ${
          alertStatus === 'normal' ? 'bg-green-500/20 border-green-500/50 text-green-400' :
          alertStatus === 'warning' ? 'bg-yellow-500/20 border-yellow-500/50 text-yellow-400' :
          alertStatus === 'alert' ? 'bg-red-500/20 border-red-500/50 text-red-400' :
          'bg-blue-500/20 border-blue-500/50 text-blue-400'
        }`}>
          <div className={`w-2 h-2 rounded-full ${
            alertStatus === 'normal' ? 'bg-green-400' :
            alertStatus === 'warning' ? 'bg-yellow-400 animate-pulse' :
            alertStatus === 'alert' ? 'bg-red-400 animate-pulse' :
            'bg-blue-400 animate-pulse'
          }`}></div>
          <span className="font-bold tracking-wide">
            {alertStatus === 'normal' ? 'MONITORING' :
             alertStatus === 'warning' ? 'WARNING' :
             alertStatus === 'alert' ? 'ALERT' :
             'OVERRIDE'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default SafetyAlert;
