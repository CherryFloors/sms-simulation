# sms-simulation

Simulate sending SMS messages

## Quickstart

1. **Install Dependencies** - This project uses poetry so dependencies and the `sms` cli can be installed by running:

```bash
poetry install
```

2. **Configure** - An example configuration, `sms_config.toml`, is included in the project root. This can be used to run
a simulation or toml with the following contents can be used to override the default config values:

```toml
[sms-simulation]
senders = 4
messages = 1000
failure_rate = 0.1
mean_send_time = 0.1
sdev_send_time = 0.025
refresh = 0.5
```

3. **Run** - The simulation can be started with default settings using the `sms` cli via the following command:

```bash
sms run
```

To specify a config file, use the `--config` flag

```bash
sms run --config <file>
```

To see help settings:
```bash
sms run --help
```

## Development Tasks

Static type checking and unit tests can be performed by running the following commnds

```bash
inv validate
```

```bash
inv test
```
