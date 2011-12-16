#!/usr/bin/python2.4
#
# Copyright 2009 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Parser."""

import re
import regexes


class UserAgent(object):
  def __init__(self, user_agent_string, js_user_agent_string=None):
    self.user_agent_string = user_agent_string
    self.js_user_agent_string = js_user_agent_string
    for ua_parser in regexes.USER_AGENT_PARSERS:
      family, v1, v2, v3 = ua_parser.Parse(user_agent_string)
      if family:
        break

    if js_user_agent_string and user_agent_string.find('chromeframe') > -1:
      family = 'Chrome Frame (%s %s)' % (family, v1)
      cf_family, v1, v2, v3 = cls.parse(js_user_agent_string)

    self.family = family or 'Other'
    self.v1 = v1
    self.v2 = v2
    self.v3 = v3

  def pretty(self):
    return UserAgent.pretty_print(self.family, self.v1, self.v2, self.v3)

  @staticmethod
  def parse_pretty(pretty_string):
    """Parse a user agent pretty (e.g. 'Chrome 4.0.203') to parts.

    Args:
      pretty_string: a user agent pretty string (e.g. 'Chrome 4.0.203')
    Returns:
      [family, v1, v2, v3] e.g. ['Chrome', '4', '0', '203']
    """
    v1, v2, v3 = None, None, None
    family, sep, version_str = pretty_string.rpartition(' ')
    if not family:
      family = version_str
    else:
      version_bits = version_str.split('.')
      v1 = version_bits.pop(0)
      if not v1.isdigit():
        family = pretty_string
        v1 = None
      elif version_bits:
        v2 = version_bits.pop(0)
        if not v2.isdigit():
          nondigit_index = min(i for i, c in enumerate(v2) if not c.isdigit())
          v2, v3 = v2[:nondigit_index], v2[nondigit_index:]
        elif version_bits:
          v3 = version_bits.pop(0)
    return family, v1, v2, v3


  @staticmethod
  def pretty_print(family, v1=None, v2=None, v3=None):
    """Pretty browser string."""
    if v3:
      if v3[0].isdigit():
        return '%s %s.%s.%s' % (family, v1, v2, v3)
      else:
        return '%s %s.%s%s' % (family, v1, v2, v3)
    elif v2:
      return '%s %s.%s' % (family, v1, v2)
    elif v1:
      return '%s %s' % (family, v1)
    return family


class UserAgentParser(object):
  def __init__(self, pattern, family_replacement=None, v1_replacement=None):
    """Initialize UserAgentParser.

    Args:
      pattern: a regular expression string
      family_replacement: a string to override the matched family (optional)
      v1_replacement: a string to override the matched v1 (optional)
    """
    self.pattern = pattern
    self.user_agent_re = re.compile(self.pattern)
    self.family_replacement = family_replacement
    self.v1_replacement = v1_replacement

  def MatchSpans(self, user_agent_string):
    match_spans = []
    match = self.user_agent_re.search(user_agent_string)
    if match:
      match_spans = [match.span(group_index)
                     for group_index in range(1, match.lastindex + 1)]
    return match_spans

  def Parse(self, user_agent_string):
    family, v1, v2, v3 = None, None, None, None
    match = self.user_agent_re.search(user_agent_string)
    if match:
      if self.family_replacement:
        if re.search(r'\$1', self.family_replacement):
          family = re.sub(r'\$1', match.group(1), self.family_replacement)
        else:
          family = self.family_replacement
      else:
        family = match.group(1)

      if self.v1_replacement:
        v1 = self.v1_replacement
      elif match.lastindex >= 2:
        v1 = match.group(2)
      if match.lastindex >= 3:
        v2 = match.group(3)
        if match.lastindex >= 4:
          v3 = match.group(4)
    return family, v1, v2, v3
