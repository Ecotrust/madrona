# -*- coding: utf-8 -*-
# Copyright 2007, 2008,2009 by Benoît Chesneau <benoitc@e-engura.org>
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
from django.dispatch import Signal

# RDH 2023-06-07: This may be hacky since I don't know offhand what signal is used for
# but in reviving ForestPlanner I just needed this to compile. So I did this below:
# https://stackoverflow.com/a/70505629/706797

# a new user has been registered
# oid_register = Signal(providing_args=['openid'])
# oid_register = Signal('openid')
oid_register = Signal()

# a new openid has been associated
# oid_associate = Signal(providing_args=["user", "openid"])
# oid_associate = Signal("user", "openid")
oid_associate = Signal()
