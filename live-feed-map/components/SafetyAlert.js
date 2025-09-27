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
    <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 shadow-xl">
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${
            alertStatus === 'normal' ? 'bg-emerald-500' :
            alertStatus === 'warning' ? 'bg-amber-500' :
            alertStatus === 'alert' ? 'bg-red-500' :
            'bg-blue-500'
          } ${alertStatus !== 'normal' ? 'animate-pulse' : ''}`}></div>
          <h3 className="text-lg font-semibold text-white">Safety Monitor</h3>
        </div>
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${
          alertStatus === 'normal' ? 'bg-emerald-500/20 text-emerald-400' :
          alertStatus === 'warning' ? 'bg-amber-500/20 text-amber-400' :
          alertStatus === 'alert' ? 'bg-red-500/20 text-red-400' :
          'bg-blue-500/20 text-blue-400'
        }`}>
          {getStatusText()}
        </div>
      </div>

      {/* Firefighter ID and Status */}
      <div className="mb-6 p-4 bg-white/5 rounded-lg border border-white/10">
        <div className="text-xs text-gray-400 mb-2 font-medium">Firefighter ID</div>
        <div className="text-lg font-mono text-white font-semibold mb-2">{firefighterId}</div>
        <div className="text-sm text-gray-300">
          Last Activity: {Math.floor(inactivityTimer / 1000)}s ago
        </div>
      </div>

      {/* Manual Check-in Button */}
      <div className="mb-6">
        <button
          onClick={handleManualCheckIn}
          disabled={alertStatus === 'override'}
          className={`w-full py-4 px-6 rounded-xl text-base font-semibold transition-all duration-200 ${
            alertStatus === 'override' 
              ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' 
              : 'bg-emerald-500 hover:bg-emerald-600 text-white shadow-lg hover:shadow-xl transform hover:scale-[1.02]'
          } disabled:opacity-50 disabled:cursor-not-allowed`}
        >
          {alertStatus === 'override' ? '✓ Check-in Confirmed' : 'Manual Check-in'}
        </button>
        {alertStatus === 'override' && (
          <div className="text-sm text-blue-400 text-center mt-3 font-medium">
            Override logged - Timer reset
          </div>
        )}
      </div>

      {/* Alert Status Display */}
      {isActive && alertStatus === 'alert' && (
        <div className="mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-xl">
          <div className="text-sm text-red-400 font-semibold mb-2">⚠️ Automatic Alert Triggered</div>
          <div className="text-base text-red-300 mb-2">
            No movement detected for {Math.floor(inactivityTimer / 1000)} seconds
          </div>
          <div className="text-sm text-red-400">
            Press "Manual Check-in" if firefighter is safe
          </div>
        </div>
      )}

      {/* Override Statistics */}
      <div className="text-sm text-gray-400 space-y-2 mb-6">
        <div className="flex justify-between">
          <span>Manual Overrides:</span>
          <span className="text-white font-medium">{overrideCount}</span>
        </div>
        {lastOverride && (
          <div className="flex justify-between">
            <span>Last Override:</span>
            <span className="text-white font-medium">{new Date(lastOverride).toLocaleTimeString()}</span>
          </div>
        )}
      </div>

      {/* Test Mode Controls */}
      <div className="p-4 bg-white/5 rounded-xl border border-white/10">
        <div className="flex items-center justify-between mb-4">
          <div className="text-sm text-gray-300 font-medium">Test Mode</div>
          <button
            onClick={handleTestMode}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              isTestMode 
                ? 'bg-amber-500 hover:bg-amber-600 text-white' 
                : 'bg-white/10 hover:bg-white/20 text-gray-300'
            }`}
          >
            {isTestMode ? 'Exit Test' : 'Test Mode'}
          </button>
        </div>
        
        {isTestMode && (
          <div className="space-y-4">
            <div className="text-sm text-gray-400 mb-3">Simulate Emergency Scenarios:</div>
            <div className="grid grid-cols-1 gap-2">
              <button
                onClick={() => handleTestScenario('normal')}
                className={`px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                  testScenario === 'normal' 
                    ? 'bg-emerald-500 text-white' 
                    : 'bg-white/10 hover:bg-white/20 text-gray-300'
                }`}
              >
                Normal Operation
              </button>
              <button
                onClick={() => handleTestScenario('stuck')}
                className={`px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                  testScenario === 'stuck' 
                    ? 'bg-amber-500 text-white' 
                    : 'bg-white/10 hover:bg-white/20 text-gray-300'
                }`}
              >
                Firefighter Stuck (Warning)
              </button>
              <button
                onClick={() => handleTestScenario('passed_out')}
                className={`px-4 py-3 rounded-lg text-sm font-medium transition-all ${
                  testScenario === 'passed_out' 
                    ? 'bg-red-500 text-white' 
                    : 'bg-white/10 hover:bg-white/20 text-gray-300'
                }`}
              >
                Firefighter Passed Out (Alert)
              </button>
            </div>
            <div className="text-sm text-gray-500 mt-3 p-3 bg-white/5 rounded-lg">
              {testScenario === 'normal' && 'Simulating normal movement patterns'}
              {testScenario === 'stuck' && 'Simulating infrequent movement (firefighter stuck)'}
              {testScenario === 'passed_out' && 'Simulating no movement (firefighter unconscious)'}
            </div>
          </div>
        )}
      </div>

      {/* Status Indicators */}
      <div className="flex justify-center mt-6">
        <div className={`flex items-center gap-3 px-4 py-3 rounded-xl ${
          alertStatus === 'normal' ? 'bg-emerald-500/10 border border-emerald-500/30 text-emerald-400' :
          alertStatus === 'warning' ? 'bg-amber-500/10 border border-amber-500/30 text-amber-400' :
          alertStatus === 'alert' ? 'bg-red-500/10 border border-red-500/30 text-red-400' :
          'bg-blue-500/10 border border-blue-500/30 text-blue-400'
        }`}>
          <div className={`w-3 h-3 rounded-full ${
            alertStatus === 'normal' ? 'bg-emerald-500' :
            alertStatus === 'warning' ? 'bg-amber-500' :
            alertStatus === 'alert' ? 'bg-red-500' :
            'bg-blue-500'
          } ${alertStatus !== 'normal' ? 'animate-pulse' : ''}`}></div>
          <span className="font-semibold text-base">
            {alertStatus === 'normal' ? 'Monitoring' :
             alertStatus === 'warning' ? 'Warning' :
             alertStatus === 'alert' ? 'Alert' :
             'Override'}
          </span>
        </div>
      </div>
    </div>
  );
};

export default SafetyAlert;
