<p align="center">
    <img src="./img/logo.png" with="400" height="400" />
</p>

> LogClouseau inspects your logs, extracts information and sends alerts according to your conditions.

Yes, there are thousands of similar projects. But this is mine!

## How to run LogClouseau

The recommended way of running LogClouseau is by using Docker.

```bash
docker build . -t logclouseau
docker run -v your/log/files:/var/logs/logclouseau-logs -v your/config/file:/logclouseau/logclouseau.toml logclouseau:latest (make sure to mount your log files and the config files)

```

## Configuration

The configuration file uses the [toml](https://github.com/toml-lang/toml) language.

A minimal configuration file contains three sections: `channel`, `file`, `alert`.

### Channels

At the moment LogClouseau provides only a `slack` and a `debug` channels.

In the provided example configuration file you'll find an example to configure both.

### Files

TODO

### Alerts

TODO


## Logo

Many thanks to [Ilaria Ranauro](https://www.instagram.com/ilaria.ranauro) for the amazing logo!
