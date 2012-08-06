#!/bin/bash
/usr/bin/python /var/www/performance/cgi-bin/performance.py > /var/www/performance/index.badhtml
/bin/sed '1,3d' /var/www/performance/index.badhtml > /var/www/performance/index.html
/bin/rm -f /var/www/performance/index.badhtml
