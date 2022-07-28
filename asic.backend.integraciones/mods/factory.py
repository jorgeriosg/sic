#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from mods import asic
from mods import claro
from mods import bancop
from mods import bancoc
from mods import asic_2


platform_option = {
    'claro': claro, 
    'asic': asic,
    'banco_popular' : bancop,
    'banco_occidente': bancoc,
    'asic_2': asic_2
    }


class FactoryIntegration:
    @staticmethod
    def get_integration(toAnswer, platform):
        if platform in platform_option:
            print(platform)
            print(toAnswer)
            print(platform_option[platform])
            return platform_option[platform]
        else:
            pass
        