# -*- coding: utf-8 -*-
from __future__ import (absolute_import)

import cnmc_client
from pymongo import MongoClient
from sets import Set

import click

LIST_OF_FILE_TYPES = ["SIPS2_PS_ELECTRICIDAD", "SIPS2_CONSUMOS_ELECTRICIDAD", "SIPS2_PS_GAS", "SIPS2_CONSUMOS_GAS"]

class CNMC_Utils(object):
    def __init__(self, cnmc_config, mongo_config):
	self.client = cnmc_client.Client(**cnmc_config)

	# Initialize MongoDB collections
	mongo = MongoClient("mongodb://" + mongo_config['connection_url'])
	self.collections = {
	    'cups': mongo[mongo_config['db']].giscedata_sips_ps,
	    'consumptions': mongo[mongo_config['db']].giscedata_sips_consums,

	    'destination_cups': mongo[mongo_config['db']].giscedata_sips_ps_fmtjul16,
	    'destination_consumptions': mongo[mongo_config['db']].giscedata_sips_consums_fmtjul16,
	}

    def find_CUPS_by_zip(self, zipcode):
	assert type(zipcode) in [str, unicode] and len(zipcode) == 5, "Provided zipcode '{}' is not valid".format(zipcode)

	search_params = {
	    'codi_postal': zipcode,
	}

	fields = {
	    'name': 1,
	}

	cups = Set()
	for a_cups in self.collections['cups'].find(search_params, fields):
	    cups.add(a_cups['name'])

	return cups

    def fetch_SIPS(self, cups, file_type=LIST_OF_FILE_TYPES[0], as_csv=False):
	response = self.client.fetch(cups=cups, file_type=file_type, as_csv=as_csv)
	assert not response.error
	return response.result


@click.command()
@click.option('--host', default='localhost', help='MongoDB host')
@click.option('--port', default='27017', help='MongoDB port', type=click.INT)
@click.option('--user', default=None, help='MongoDB user')
@click.option('--password', default=None, help='MongoDB password')
@click.option('--database', default='database', help='MongoDB database')
@click.argument('zipcode', type=click.STRING)
def main(zipcode, host, port, user, password, database):
    cnmc_config = {
	'environment': 'prod',
    }

    mongo_config = {
	'connection_url': "{}:{}".format(host, port),
	'db': database,
	'user': user,
	'password': password,
    }

    utils = CNMC_Utils(cnmc_config, mongo_config)
    # Initialize CNMC Client

    cups_list = utils.find_CUPS_by_zip(zipcode)

    SIPS_csv = utils.fetch_SIPS(cups=cups_list, as_csv=True)

    for line in SIPS_csv:
        print (line)


if __name__ == '__main__':
    main()
