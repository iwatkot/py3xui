"""This module contains the Server class which represents server information in XUI API."""

from pydantic import BaseModel, ConfigDict, Field


class ServerFields:
    """Stores fields returned by XUI API for parsing."""

    CPU = "cpu"
    CPU_CORES = "cpuCores"
    LOGICAL_PRO = "logicalPro"
    CPU_SPEED_MHZ = "cpuSpeedMhz"
    
    MEM_CURRENT = "current"
    MEM_TOTAL = "total"
    
    XRAY_STATE = "state"
    XRAY_ERROR_MSG = "errorMsg"
    XRAY_VERSION = "version"
    
    UPTIME = "uptime"
    LOADS = "loads"
    TCP_COUNT = "tcpCount"
    UDP_COUNT = "udpCount"
    
    NET_IO_UP = "up"
    NET_IO_DOWN = "down"
    
    NET_TRAFFIC_SENT = "sent"
    NET_TRAFFIC_RECV = "recv"
    
    PUBLIC_IP_V4 = "ipv4"
    PUBLIC_IP_V6 = "ipv6"
    
    APP_THREADS = "threads"
    APP_MEM = "mem"
    APP_UPTIME = "uptime"


class MemoryInfo(BaseModel):
    """Represents memory information.
    
    Attributes:
        current (int): Current memory usage in bytes
        total (int): Total memory capacity in bytes
    """
    current: int
    total: int


class XRayInfo(BaseModel):
    """Represents XRay status information.
    
    Attributes:
        state (str): XRay state (e.g. "running")
        error_msg (str): Error message if any
        version (str): XRay version
    """
    state: str
    error_msg: str = Field(alias=ServerFields.XRAY_ERROR_MSG)
    version: str


class NetworkIO(BaseModel):
    """Represents network I/O information.
    
    Attributes:
        up (int): Outgoing traffic
        down (int): Incoming traffic
    """
    up: int
    down: int


class NetworkTraffic(BaseModel):
    """Represents network traffic information.
    
    Attributes:
        sent (int): Sent traffic
        recv (int): Received traffic
    """
    sent: int
    recv: int


class PublicIP(BaseModel):
    """Represents public IP addresses information.
    
    Attributes:
        ipv4 (str): Public IPv4 address
        ipv6 (str): Public IPv6 address
    """
    ipv4: str
    ipv6: str


class AppStats(BaseModel):
    """Represents application statistics.
    
    Attributes:
        threads (int): Number of threads
        mem (int): Memory usage
        uptime (int): Uptime in seconds
    """
    threads: int
    mem: int
    uptime: int


class Server(BaseModel):
    """Represents server information in XUI API.

    Attributes:
        cpu (float): CPU usage percentage
        cpu_cores (int): Number of physical CPU cores
        logical_pro (int): Number of logical processors
        cpu_speed_mhz (float): CPU frequency in MHz
        mem (MemoryInfo): Memory information
        swap (MemoryInfo): Swap memory information
        disk (MemoryInfo): Disk information
        xray (XRayInfo): XRay status information
        uptime (int): Server uptime in seconds
        loads (list[float]): System load averages [1, 5, 15 minutes]
        tcp_count (int): Number of TCP connections
        udp_count (int): Number of UDP connections
        net_io (NetworkIO): Network I/O information
        net_traffic (NetworkTraffic): Network traffic information
        public_ip (PublicIP): Public IP addresses information
        app_stats (AppStats): Application statistics
    """

    cpu: float
    cpu_cores: int = Field(alias=ServerFields.CPU_CORES)
    logical_pro: int = Field(alias=ServerFields.LOGICAL_PRO)
    cpu_speed_mhz: float = Field(alias=ServerFields.CPU_SPEED_MHZ)
    
    mem: MemoryInfo
    swap: MemoryInfo
    disk: MemoryInfo
    
    xray: XRayInfo
    uptime: int
    loads: list[float]
    
    tcp_count: int = Field(alias=ServerFields.TCP_COUNT)
    udp_count: int = Field(alias=ServerFields.UDP_COUNT)
    
    net_io: NetworkIO
    net_traffic: NetworkTraffic
    public_ip: PublicIP = Field(alias="publicIP")
    app_stats: AppStats = Field(alias="appStats")

    model_config = ConfigDict(
        populate_by_name=True,
    )
