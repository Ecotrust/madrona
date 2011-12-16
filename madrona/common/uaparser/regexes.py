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

"""Regexes."""

import parser


browser_slash_v123_names = (
    'Jasmine|ANTGalio|Midori|Fresco|Lobo|Maxthon|Lynx|OmniWeb|Dillo|Camino|'
    'Demeter|Fluid|Fennec|Shiira|Sunrise|Chrome|Flock|Netscape|Lunascape|'
    'Epiphany|WebPilot|Vodafone|NetFront|Konqueror|SeaMonkey|Kazehakase|'
    'Vienna|Iceape|Iceweasel|IceWeasel|Iron|K-Meleon|Sleipnir|Galeon|'
    'GranParadiso|Opera Mini|iCab|NetNewsWire|Iron|Iris')

browser_slash_v12_names = (
    'Bolt|Jasmine|Maxthon|Lynx|Arora|IBrowse|Dillo|Camino|Shiira|Fennec|'
    'Phoenix|Chrome|Flock|Netscape|Lunascape|Epiphany|WebPilot|'
    'Opera Mini|Opera|Vodafone|'
    'NetFront|Konqueror|SeaMonkey|Kazehakase|Vienna|Iceape|Iceweasel|IceWeasel|'
    'Iron|K-Meleon|Sleipnir|Galeon|GranParadiso|'
    'iCab|NetNewsWire|Iron|Space Bison|Stainless|Orca')

_P = parser.UserAgentParser
USER_AGENT_PARSERS = (
  #### SPECIAL CASES TOP ####
  # must go before Opera
  _P(r'^(Opera)/(\d+)\.(\d+) \(Nintendo Wii', family_replacement='Wii'),
  # must go before Browser/v1.v2 - eg: Minefield/3.1a1pre
  _P(r'(Namoroka|Shiretoko|Minefield)/(\d+)\.(\d+)\.(\d+(?:pre)?)',
     'Firefox ($1)'),
  _P(r'(Namoroka|Shiretoko|Minefield)/(\d+)\.(\d+)([ab]\d+[a-z]*)?',
     'Firefox ($1)'),
  _P(r'(SeaMonkey|Fennec|Camino)/(\d+)\.(\d+)([ab]?\d+[a-z]*)'),
  # e.g.: Flock/2.0b2
  _P(r'(Flock)/(\d+)\.(\d+)(b\d+?)'),

  # e.g.: Fennec/0.9pre
  _P(r'(Fennec)/(\d+)\.(\d+)(pre)'),
  _P(r'(Navigator)/(\d+)\.(\d+)\.(\d+)', 'Netscape'),
  _P(r'(Navigator)/(\d+)\.(\d+)([ab]\d+)', 'Netscape'),
  _P(r'(Netscape6)/(\d+)\.(\d+)\.(\d+)', 'Netscape'),
  _P(r'(MyIBrow)/(\d+)\.(\d+)', 'My Internet Browser'),
  _P(r'(Firefox).*Tablet browser (\d+)\.(\d+)\.(\d+)', 'MicroB'),
  # Opera will stop at 9.80 and hide the real version in the Version string.
  # see: http://dev.opera.com/articles/view/opera-ua-string-changes/
  _P(r'(Opera)/9.80.*Version\/(\d+)\.(\d+)(?:\.(\d+))?'),

  _P(r'(Firefox)/(\d+)\.(\d+)\.(\d+(?:pre)?) \(Swiftfox\)', 'Swiftfox'),
  _P(r'(Firefox)/(\d+)\.(\d+)([ab]\d+[a-z]*)? \(Swiftfox\)', 'Swiftfox'),

  # catches lower case konqueror
  _P(r'(konqueror)/(\d+)\.(\d+)\.(\d+)', 'Konqueror'),

  #### END SPECIAL CASES TOP ####

  #### MAIN CASES - this catches > 50% of all browsers ####
  # Browser/v1.v2.v3
  _P(r'(%s)/(\d+)\.(\d+)\.(\d+)' % browser_slash_v123_names),
  # Browser/v1.v2
  _P(r'(%s)/(\d+)\.(\d+)' % browser_slash_v12_names),
  # Browser v1.v2.v3 (space instead of slash)
  _P(r'(iRider|Crazy Browser|SkipStone|iCab|Lunascape|Sleipnir|Maemo Browser) (\d+)\.(\d+)\.(\d+)'),
  # Browser v1.v2 (space instead of slash)
  _P(r'(iCab|Lunascape|Opera|Android) (\d+)\.(\d+)'),
  _P(r'(IEMobile) (\d+)\.(\d+)', 'IE Mobile'),
  # DO THIS AFTER THE EDGE CASES ABOVE!
  _P(r'(Firefox)/(\d+)\.(\d+)\.(\d+)'),
  _P(r'(Firefox)/(\d+)\.(\d+)(pre|[ab]\d+[a-z]*)?'),
  #### END MAIN CASES ####

  #### SPECIAL CASES ####
  #_P(r''),
  _P(r'(Obigo|OBIGO)[^\d]*(\d+)(?:.(\d+))?', 'Obigo'),
  _P(r'(MAXTHON|Maxthon) (\d+)\.(\d+)', family_replacement='Maxthon'),
  _P(r'(Maxthon|MyIE2|Uzbl|Shiira)', v1_replacement='0'),
  _P(r'(PLAYSTATION) (\d+)', family_replacement='PlayStation'),
  _P(r'(PlayStation Portable)[^\d]+(\d+).(\d+)'),
  _P(r'(BrowseX) \((\d+)\.(\d+)\.(\d+)'),
  _P(r'(Opera)/(\d+)\.(\d+).*Opera Mobi', 'Opera Mobile'),
  _P(r'(POLARIS)/(\d+)\.(\d+)', family_replacement='Polaris'),
  _P(r'(BonEcho)/(\d+)\.(\d+)\.(\d+)', 'Bon Echo'),
  _P(r'(iPhone) OS (\d+)_(\d+)(?:_(\d+))?'),
  _P(r'(Avant)', v1_replacement='1'),
  _P(r'(Nokia)[EN]?(\d+)'),
  _P(r'(Black[bB]erry)(\d+)', family_replacement='Blackberry'),
  _P(r'(OmniWeb)/v(\d+)\.(\d+)'),
  _P(r'(Blazer)/(\d+)\.(\d+)', 'Palm Blazer'),
  _P(r'(Pre)/(\d+)\.(\d+)', 'Palm Pre'),
  _P(r'(Links) \((\d+)\.(\d+)'),
  _P(r'(QtWeb) Internet Browser/(\d+)\.(\d+)'),
  _P(r'(Version)/(\d+)\.(\d+)(?:\.(\d+))?.*Safari/',
     family_replacement='Safari'),
  _P(r'(OLPC)/Update(\d+)\.(\d+)'),
  _P(r'(OLPC)/Update()\.(\d+)', v1_replacement='0'),
  _P(r'(SamsungSGHi560)', family_replacement='Samsung SGHi560'),
  _P(r'^(SonyEricssonK800i)', family_replacement='Sony Ericsson K800i'),
  _P(r'(Teleca Q7)'),
  _P(r'(MSIE) (\d+)\.(\d+)', family_replacement='IE'),
)

