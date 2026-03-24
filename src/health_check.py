"""Health check and system monitoring."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from typing import Dict, Optional
import asyncio


class HealthStatus(Enum):
    """Health status enumeration."""
    HEALTHY = "healthy"
    WARNING = "warning"
    UNHEALTHY = "unhealthy"


@dataclass
class ComponentHealth:
    """Health status of a single component."""
    name: str
    status: HealthStatus
    message: str = ""
    last_check: datetime = field(default_factory=datetime.utcnow)
    response_time_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "status": self.status.value,
            "message": self.message,
            "last_check": self.last_check.isoformat(),
            "response_time_ms": self.response_time_ms
        }


class HealthChecker:
    """Health check coordinator."""
    
    def __init__(self):
        self.components: Dict[str, ComponentHealth] = {}
    
    async def check_api_health(self) -> ComponentHealth:
        """Check API health."""
        start = datetime.utcnow()
        try:
            # Simple check - if this code is running, API is up
            await asyncio.sleep(0.001)
            elapsed = (datetime.utcnow() - start).total_seconds() * 1000
            return ComponentHealth(
                name="api",
                status=HealthStatus.HEALTHY,
                message="API is running",
                response_time_ms=elapsed
            )
        except Exception as e:
            return ComponentHealth(
                name="api",
                status=HealthStatus.UNHEALTHY,
                message=f"API check failed: {str(e)}"
            )
    
    async def check_database_health(self) -> ComponentHealth:
        """Check database health."""
        # TODO: Implement actual database health check
        return ComponentHealth(
            name="database",
            status=HealthStatus.HEALTHY,
            message="Database OK (mock)"
        )
    
    async def check_cache_health(self) -> ComponentHealth:
        """Check cache health."""
        # TODO: Implement Redis health check
        return ComponentHealth(
            name="cache",
            status=HealthStatus.HEALTHY,
            message="Cache OK (mock)"
        )
    
    async def check_data_service_health(self) -> ComponentHealth:
        """Check data service health."""
        # TODO: Implement actual data service health check
        return ComponentHealth(
            name="data_service",
            status=HealthStatus.HEALTHY,
            message="Data service OK (mock)"
        )
    
    async def run_all_checks(self) -> Dict[str, ComponentHealth]:
        """Run all health checks."""
        checks = [
            self.check_api_health(),
            self.check_database_health(),
            self.check_cache_health(),
            self.check_data_service_health()
        ]
        
        results = await asyncio.gather(*checks)
        self.components = {ch.name: ch for ch in results}
        return self.components
    
    def get_overall_health(self) -> HealthStatus:
        """Get overall system health."""
        if not self.components:
            return HealthStatus.HEALTHY
        
        statuses = [ch.status for ch in self.components.values()]
        
        if HealthStatus.UNHEALTHY in statuses:
            return HealthStatus.UNHEALTHY
        elif HealthStatus.WARNING in statuses:
            return HealthStatus.WARNING
        else:
            return HealthStatus.HEALTHY
    
    def get_health_report(self) -> Dict:
        """Get comprehensive health report."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "status": self.get_overall_health().value,
            "components": {name: ch.to_dict() for name, ch in self.components.items()}
        }


# Global health checker
health_checker = HealthChecker()


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance."""
    return health_checker
