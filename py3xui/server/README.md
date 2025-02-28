<a id="server.server"></a>

# server.server

This module contains the Server class which represents server information in XUI API.

<a id="server.server.ServerFields"></a>

## ServerFields Objects

```python
class ServerFields()
```

Stores fields returned by XUI API for parsing.

<a id="server.server.MemoryInfo"></a>

## MemoryInfo Objects

```python
class MemoryInfo(BaseModel)
```

Represents memory information.

**Attributes**:

- `current` _int_ - Current memory usage in bytes
- `total` _int_ - Total memory capacity in bytes

<a id="server.server.XRayInfo"></a>

## XRayInfo Objects

```python
class XRayInfo(BaseModel)
```

Represents XRay status information.

**Attributes**:

- `state` _str_ - XRay state (e.g. "running")
- `error_msg` _str_ - Error message if any
- `version` _str_ - XRay version

<a id="server.server.XRayInfo.error_msg"></a>

#### error\_msg

type: ignore

<a id="server.server.NetworkIO"></a>

## NetworkIO Objects

```python
class NetworkIO(BaseModel)
```

Represents network I/O information.

**Attributes**:

- `up` _int_ - Outgoing traffic
- `down` _int_ - Incoming traffic

<a id="server.server.NetworkTraffic"></a>

## NetworkTraffic Objects

```python
class NetworkTraffic(BaseModel)
```

Represents network traffic information.

**Attributes**:

- `sent` _int_ - Sent traffic
- `recv` _int_ - Received traffic

<a id="server.server.PublicIP"></a>

## PublicIP Objects

```python
class PublicIP(BaseModel)
```

Represents public IP addresses information.

**Attributes**:

- `ipv4` _str_ - Public IPv4 address
- `ipv6` _str_ - Public IPv6 address

<a id="server.server.AppStats"></a>

## AppStats Objects

```python
class AppStats(BaseModel)
```

Represents application statistics.

**Attributes**:

- `threads` _int_ - Number of threads
- `mem` _int_ - Memory usage
- `uptime` _int_ - Uptime in seconds

<a id="server.server.Server"></a>

## Server Objects

```python
class Server(BaseModel)
```

Represents server information in XUI API.

**Attributes**:

- `cpu` _float_ - CPU usage percentage
- `cpu_cores` _int_ - Number of physical CPU cores
- `logical_pro` _int_ - Number of logical processors
- `cpu_speed_mhz` _float_ - CPU frequency in MHz
- `mem` _MemoryInfo_ - Memory information
- `swap` _MemoryInfo_ - Swap memory information
- `disk` _MemoryInfo_ - Disk information
- `xray` _XRayInfo_ - XRay status information
- `uptime` _int_ - Server uptime in seconds
- `loads` _list[float]_ - System load averages [1, 5, 15 minutes]
- `tcp_count` _int_ - Number of TCP connections
- `udp_count` _int_ - Number of UDP connections
- `net_io` _NetworkIO_ - Network I/O information
- `net_traffic` _NetworkTraffic_ - Network traffic information
- `public_ip` _PublicIP_ - Public IP addresses information
- `app_stats` _AppStats_ - Application statistics

<a id="server.server.Server.cpu"></a>

#### cpu

type: ignore

<a id="server.server.Server.cpu_cores"></a>

#### cpu\_cores

type: ignore

<a id="server.server.Server.logical_pro"></a>

#### logical\_pro

type: ignore

<a id="server.server.Server.cpu_speed_mhz"></a>

#### cpu\_speed\_mhz

type: ignore

<a id="server.server.Server.tcp_count"></a>

#### tcp\_count

type: ignore

<a id="server.server.Server.udp_count"></a>

#### udp\_count

type: ignore

<a id="server.server.Server.net_io"></a>

#### net\_io

type: ignore

<a id="server.server.Server.net_traffic"></a>

#### net\_traffic

type: ignore

<a id="server.server.Server.public_ip"></a>

#### public\_ip

type: ignore

<a id="server.server.Server.app_stats"></a>

#### app\_stats

type: ignore

