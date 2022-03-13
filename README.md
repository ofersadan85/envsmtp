# envsmtp
[![Latest Release](https://img.shields.io/github/v/release/ofersadan85/envsmtp)](https://github.com/ofersadan85/envsmtp/releases/latest)
[![envsmtp on pypi](https://img.shields.io/pypi/v/envsmtp)](https://pypi.org/project/envsmtp/)
[![MIT License](https://img.shields.io/github/license/ofersadan85/envsmtp)](LICENSE)
[![unittests Status](https://img.shields.io/github/workflow/status/ofersadan85/envsmtp/Python%20package%20tests?label=tests)](tests)

Simple sending of smtp emails using environment     variables

## Install
[![envsmtp on pypi](https://img.shields.io/pypi/v/envsmtp)](https://pypi.org/project/envsmtp/)
![](https://img.shields.io/pypi/wheel/envsmtp)

    pip install --upgrade envsmtp

## Environment Variables
You must set `SMTP_USER` and `SMTP_PASS` in your environment with your user and password!

See additional optional settings in [example.env](example.env)

## Usage
This package will by default use STARTTLS settings for `smtp.gmail.com` on port 587. If you wish to change these settings, you can set your own environment variables for `SMTP_HOST` and `SMTP_PORT`

Once installed, here's a simple example of how to use this package:

    from envsmtp import EmailMessage

    msg = EmailMessage(
        sender="sender@example.com",
        receipients="receipient@example.com",
        subject="envsmtp test",
        body="This is just a test message",
    )
    msg.smtp_send()

To send with attachments:

    from envsmtp import EmailMessage, EmailAttachment

    attachments = [
        EmailAttachment(content='/path/to/file.txt'),
        EmailAttachment(content=b'randombytes', filename='bytes_test.txt'),
        EmailAttachment(content='/path/to/another.txt', filename='this_name_is_different_.txt')
    ]
    msg = EmailMessage(
        sender="sender@example.com",
        receipients="receipient@example.com",
        subject="envsmtp test",
        body="This is just a test message",
        attachments=attachments,
    )
    msg.smtp_send()

## Requirements

![](https://img.shields.io/pypi/pyversions/envsmtp)

Tested with & designed for python 3.10, see [requirements.txt](requirements.txt) for additional dependencies

## Contributing

For bugs / feature requests please submit [issues](https://github.com/ofersadan85/envsmtp/issues)

[![Open Issues](https://img.shields.io/github/issues-raw/ofersadan85/envsmtp)](https://github.com/ofersadan85/envsmtp/issues)
[![Closed Issues](https://img.shields.io/github/issues-closed-raw/ofersadan85/envsmtp)](https://github.com/ofersadan85/envsmtp/issues)

If you would like to contribute to this project, you are welcome
to [submit a pull request](https://github.com/ofersadan85/envsmtp/pulls)

[![Open Pull Requests](https://img.shields.io/github/issues-pr-raw/ofersadan85/envsmtp)](https://github.com/ofersadan85/envsmtp/pulls)
[![Closed Pull Requests](https://img.shields.io/github/issues-pr-closed-raw/ofersadan85/envsmtp)](https://github.com/ofersadan85/envsmtp/pulls)

## Warranty / Liability / Official support

This project is being developed independently, we provide the
package "as-is" without any implied warranty or liability, usage is your own responsibility

## Additional info

Just because I like badges

![](https://img.shields.io/github/languages/code-size/ofersadan85/envsmtp)
![Pypi downloads per month](https://img.shields.io/pypi/dm/envsmtp?label=pypi%20downloads)
![Pypi downloads per week](https://img.shields.io/pypi/dw/envsmtp?label=pypi%20downloads)
![Pypi downloads per day](https://img.shields.io/pypi/dd/envsmtp?label=pypi%20downloads)