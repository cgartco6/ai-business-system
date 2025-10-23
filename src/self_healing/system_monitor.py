import psutil
import logging
import time
from datetime import datetime, timedelta
import threading

class SystemMonitor:
    def __init__(self):
        self.performance_metrics = {}
        self.health_thresholds = {
            'cpu_percent': 80,
            'memory_percent': 85,
            'disk_percent': 90,
            'response_time': 5.0  # seconds
        }
        self.monitoring_active = True
        
    def start_continuous_monitoring(self):
        """Start continuous system monitoring"""
        def monitor_loop():
            while self.monitoring_active:
                try:
                    self.collect_system_metrics()
                    self.check_system_health()
                    time.sleep(60)  # Check every minute
                except Exception as e:
                    logging.error(f"Monitoring error: {e}")
                    time.sleep(300)  # Wait 5 minutes on error
        
        monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        monitor_thread.start()
        logging.info("Continuous system monitoring started")
    
    def collect_system_metrics(self):
        """Collect comprehensive system metrics"""
        metrics = {
            'timestamp': datetime.now(),
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent,
            'network_io': psutil.net_io_counters(),
            'active_processes': len(psutil.pids()),
            'system_uptime': time.time() - psutil.boot_time()
        }
        
        # Store metrics with timestamp
        current_time = datetime.now()
        self.performance_metrics[current_time] = metrics
        
        # Clean up old metrics (keep last 24 hours)
        self._cleanup_old_metrics()
        
        return metrics
    
    def check_system_health(self):
        """Check system health against thresholds"""
        current_metrics = self.collect_system_metrics()
        alerts = []
        
        # CPU Check
        if current_metrics['cpu_percent'] > self.health_thresholds['cpu_percent']:
            alerts.append(f"High CPU usage: {current_metrics['cpu_percent']}%")
        
        # Memory Check
        if current_metrics['memory_percent'] > self.health_thresholds['memory_percent']:
            alerts.append(f"High memory usage: {current_metrics['memory_percent']}%")
        
        # Disk Check
        if current_metrics['disk_percent'] > self.health_thresholds['disk_percent']:
            alerts.append(f"High disk usage: {current_metrics['disk_percent']}%")
        
        # Log alerts and trigger auto-recovery
        for alert in alerts:
            logging.warning(f"System alert: {alert}")
            self.trigger_auto_recovery(alert)
        
        return alerts
    
    def trigger_auto_recovery(self, alert):
        """Trigger appropriate auto-recovery based on alert"""
        if "CPU" in alert:
            self.optimize_cpu_usage()
        elif "memory" in alert:
            self.optimize_memory_usage()
        elif "disk" in alert:
            self.cleanup_disk_space()
    
    def optimize_cpu_usage(self):
        """Optimize CPU usage by adjusting worker processes"""
        logging.info("Optimizing CPU usage...")
        # Implementation would adjust concurrent processes
        # based on current load and available resources
    
    def optimize_memory_usage(self):
        """Optimize memory usage by clearing caches"""
        logging.info("Optimizing memory usage...")
        # Implementation would clear unnecessary caches
        # and optimize data structures
    
    def cleanup_disk_space(self):
        """Clean up disk space by removing temporary files"""
        logging.info("Cleaning up disk space...")
        # Implementation would remove old logs, cache files, etc.
    
    def _cleanup_old_metrics(self):
        """Remove metrics older than 24 hours"""
        cutoff_time = datetime.now() - timedelta(hours=24)
        old_keys = [k for k in self.performance_metrics.keys() if k < cutoff_time]
        for key in old_keys:
            del self.performance_metrics[key]
    
    def get_performance_report(self):
        """Generate performance report"""
        if not self.performance_metrics:
            return {}
        
        recent_metrics = list(self.performance_metrics.values())[-10:]  # Last 10 readings
        
        report = {
            'current_status': 'healthy',
            'average_cpu': sum(m['cpu_percent'] for m in recent_metrics) / len(recent_metrics),
            'average_memory': sum(m['memory_percent'] for m in recent_metrics) / len(recent_metrics),
            'system_uptime_days': recent_metrics[-1]['system_uptime'] / 86400,
            'alerts_in_last_hour': len([k for k in self.performance_metrics.keys() 
                                      if k > datetime.now() - timedelta(hours=1)])
        }
        
        # Determine overall status
        if (report['average_cpu'] > 70 or report['average_memory'] > 75):
            report['current_status'] = 'degraded'
        elif (report['average_cpu'] > 85 or report['average_memory'] > 90):
            report['current_status'] = 'critical'
        
        return report
