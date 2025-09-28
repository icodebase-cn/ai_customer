# Stress Testing Instructions

## Setup
1. Install dependencies:
```bash
pip install -r stress_test/requirements.txt
```

2. Add a real test image:
```bash
cp path/to/your/image.jpg stress_test/test_data/sample.jpg
```

## Running Tests
### Web UI Mode (Recommended)
1. Start the FastAPI server in one terminal:
```bash
python run.py
```

2. Start Locust in another terminal:
```bash
cd stress_test
locust -f locustfile.py
```

3. Open Locust web UI at `http://localhost:8089`

4. Configure test parameters:
   - Number of users: 1000
   - Spawn rate: 100
   - Host: `http://localhost:8000`

5. Click "Start swarming" to begin test
6. Monitor real-time statistics:
   - Charts: Requests/s, Response times, User count
   - Tables: Failure rates, Response percentiles

### Headless Mode (No UI)
1. Start FastAPI server:
```bash
python run.py
```

2. Run Locust with CLI parameters:
```bash
cd stress_test
locust -f locustfile.py --headless --users 1 --spawn-rate 1 --run-time 1m --host http://192.168.1.167:8000
```

Parameters:
- `--headless`: Run without web UI
- `--users`: Total number of users
- `--spawn-rate`: Users spawned per second
- `--run-time`: Test duration (1m, 5m, 1h)
- `--host`: Target server URL

## Understanding Results
- **Response Times**: Should be under 500ms for good performance
- **Failure Rate**: Should be below 1% for stable service
- **RPS (Requests per Second)**: Measures throughput capacity
- **Percentiles (50%, 95%)**: Show typical and worst-case response times

![Locust UI](https://locust.io/static/img/screenshot-stats.png)

## Logging Configuration
By default, Locust logs at INFO level. To enable debug logging:

1. Create `locust_logging.conf`:
```ini
[loggers]
keys=root,locust

[handlers]
keys=console

[formatters]
keys=standard

[logger_root]
level=DEBUG
handlers=console

[logger_locust]
level=DEBUG
handlers=console
qualname=locust
propagate=0

[handler_console]
class=StreamHandler
level=DEBUG
formatter=standard
args=(sys.stdout,)

[formatter_standard]
format=%(asctime)s [%(levelname)s] %(name)s: %(message)s
datefmt=%Y-%m-%d %H:%M:%S
```

2. Run Locust with logging config:
```bash
locust -f locustfile.py --logfile locust.log --loglevel DEBUG --logconf locust_logging.conf
```

This will provide detailed request/response logs in `locust.log`.

## Troubleshooting
### Connection Refused Errors
If you see `[WinError 10061] 由于目标计算机积极拒绝，无法连接`:

1. Verify API server is running:
```bash
curl http://localhost:8000/api/health
# Should return: {"status":"healthy","service":"多语言智能客服"}
```

2. Check server port:
```bash
netstat -ano | findstr :8000
# Should show LISTENING state
```

3. Confirm Locust host configuration:
   - Web UI: Set Host to `http://localhost:8000`
   - CLI: Include `--host http://localhost:8000`

4. Check firewall settings:
```bash
netsh advfirewall firewall show rule name=all | findstr 8000
```
If blocked, add exception:
```bash
netsh advfirewall firewall add rule name="Allow Port 8000" dir=in action=allow protocol=TCP localport=8000
```

### Other Common Issues
- "No tests running": Click "Start swarming" in web UI
- "Image not found": Check `stress_test/test_data/sample.jpg` exists
- "0 requests": Verify test parameters and server availability
- High failure rate: Check API server logs for errors
- "Missing responses": Enable debug logging as shown above