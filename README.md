<p align="center">
    <img src="./img/logo.png" with="400" height="400" />
</p>

> LogClouseau inspects your logs, extracts information and sends alerts according to your conditions.

Yes, there are thousands of similar projects. But this is mine!

## How to run LogClouseau

The recommended way of running LogClouseau is by using Docker.
Make sure to mount both the log files and a suitable LogClouseau configuration file.

```bash
docker build . -t logclouseau
docker run -v your/log/files:/var/logs/logclouseau-logs -v your/config/file:/logclouseau/logclouseau.toml logclouseau:latest
```

## Configuration

The configuration file uses the [toml](https://github.com/toml-lang/toml) language.

A minimal configuration file contains three sections: `channel`, `file`, `alert`, each of which should contain at least one element (e.g. `channel.default_channel`)

### Channels

At the moment LogClouseau provides only a `slack` and a `debug` channels.

In the provided example configuration file you'll find an example to configure both.

### Files

Create a file block for each monitored file. Each file needs a `path` property and a `tokens` property.

The `tokens` property is needed to extract information from each log line. Lines which doesn't match the tokens will be ignored.

For example the `combined` nginx log line, which looks like this:

```
66.249.65.3 - - [06/Nov/2014:19:11:24 +0600] "GET /?q=%E0%A6%AB%E0%A6%BE%E0%A7%9F%E0%A6%BE%E0%A6%B0 HTTP/1.1" 200 4223 "-" "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
```

can be parsed with the following configuration block:

```
[file.nginx_access_log]
"path" = "/var/log/nginx/access.log"
"tokens" = '"{ip} - - [{date}] "{request}" {response_code} {response_size} "{referer}" "{user_agent}"'
```

Each extracted variable is available in the alert block for the `identifier`, `conditions`, `message` properties.

### Alert

Each alerts has several properties:

| property | description | default |
|---|---|---|
| `file | Reference to a file definition (in the previous example it would be `"nginx_access_log"`) | - (no default) |
| `channel` | Reference to a channel definition | `"debug"` (that's why it's a good practice to define at least a channel with that name) |
| `condition` | String that gets `eval`uated by python in order to understand whether to send an alert or not. Internally it's possible to use the token previously defined as variables. For example, to receive an alert for every 404 returned to a given IP, the condition would be `"response_code = '404' and ip = '1.2.3.4'"`. Remember that all the variables are strings! | `"True"` (an alert is sent for every line) |
| `identifier` | String that gets `eval`uated by python. Having different identifiers is useful to have different `min_occurrences` and `grace`. For example, if my identifier is `"'ident-' + ip"` and the grace period is `{hours = 1}` I won't send more than an alert per hour regarding the same IP | defaults to the alert name |
| `grace` | Grace period definition: during that period after sending an alert, no second alert with the same identifier will be sent. It can be expressed by a table (dictionary) which might contain the properties: days, seconds, minutes, hours, weeks. | `{days = 0}` (no grace) |
| `min_occurrences` | Number of times that an error has to occur before an alert is sent | `1` (alerts are immediately sent) |
| `message` | The content of the alert message. Also this string gets `eval`uated by python, so remember to enclose it in quotes (e.g. `"'Alert!'"`) | `"'Alert! ' + alert_name"` |

## Acknowledegments

Many thanks to [Ilaria Ranauro](https://www.instagram.com/ilaria.ranauro) for the amazing logo, and to [Michał Wachowski](https://github.com/potfur) for his precious "pythonic" suggestions.
