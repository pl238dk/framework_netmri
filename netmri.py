import requests
requests.packages.urllib3.disable_warnings()
import json
import os
import xml.etree.ElementTree as x

'''
{
	'success': False,
	'result': '',
	'response':response,
}
'''

class NetMRI(object):
	version = '3.8'
	proxies = {
		'http':	'',
		'https':	'',
	}
	def __init__(self, config):
		self.config = config
		self.auth = False
		creds = self.load_configuration(config)
		if not creds:
			print('[W] Credentials not found in configuration file!')
		else:
			self.auth = True
			self.authenticate()
		return
	
	def load_configuration(self, config):
		'''
		if config == 'custom':
			#Requires:
			#	host - NetMRI collector
			#	username - SSO of user
			#	password - PIN + Token
			self.collector = params['host']
			#self.authenticate(params)
			return
		'''
		config_file = 'configuration.json'
		path = os.path.abspath(__file__)
		dir_path = os.path.dirname(path)
		with open(f'{dir_path}/{config_file}','r') as f:
			raw_file = f.read()
		config_raw = json.loads(raw_file)
		if config not in config_raw:
			print('[E] Configuration not found in configuration.json')
			self.auth = False
			return {}
		else:
			self.auth = True
			output = config_raw[config]
			self.collector = output['host']
			self.base_url = f'https://{self.collector}/api/'
			#self.authenticate(connection_info)
		return output
	
	def authenticate(self):
		creds = self.load_configuration(self.config)
		self.session = requests.Session()
		self.session.trust_env = False
		self.session.headers.update(self.proxies)
		
		authentication_params = {
			'username':	creds['username'],
			'password':	creds['password'],
		}
		self.session.params.update(authentication_params)
		
		path = 'authenticate'
		auth_url = f'{self.base_url}{path}'
		self.session.get(auth_url, verify=False)
		self.session.params = {}
		return
	
	def get(self, path, params={}):
		url = f'{self.base_url}{self.version}/{path}'
		response_raw = self.session.get(url, params=params, verify=False)
		output = {
			'success': False,
			'result': '',
			'response': response_raw,
		}
		if response_raw.status_code in [200, 201]:
			response_xml = x.fromstring(response_raw.text)
			result = self.parse_xml(response_xml)
			output['success'] = True
			output['result'] = result
		elif response_raw.status_code == 401:
			self.authenticate()
			response_raw = self.session.get(url, params=params, verify=False)
			response_xml = x.fromstring(response_raw.text)
			result = self.parse_xml(response_xml)
			output = {
				'success': False,
				'result': result,
				'response': response_raw,
			}
			return output
		else:
			pass
		return output
	
	def job_create(self, params):
		#params = {
		#	'name':	'something descriptive',
		#	'description':	'something more detailed',
		#	# cron format
		#	'schedule':	'00 17 17 06 *',
		#	# Ad Hoc Command Batch
		#	'script_id':	1,
		#	'$commands_to_be_executed':	'show version\nshow version',
		#	'device_ids':	12345,
		#}
		#get('job_specifications/create', params)
		path = f'job_specifications/create.xml'
		output = self.get(path, params=params)
		return output
	
	def job_approve(self, params):
		#params = {
		#	'id': <job_id>,
		#}
		#get('job_specifications/approve', params)
		path = f'job_specifications/approve.xml'
		output = self.get(path, params=params)
		return output
	
	def job_unapprove(self, params):
		#params = {
		#	'id': <job_id>,
		#}
		#get('job_specifications/unapprove', params)
		path = f'job_specifications/unapprove.xml'
		output = self.get(path, params=params)
		return output
	
	def job_destroy(self, params):
		#params = {
		#	'id': <job_id>,
		#}
		#get('job_specifications/destroy', params)
		path = f'job_specifications/destroy.xml'
		output = self.get(path, params=params)
		return output

	def job_run(self, params):
		#params = {
		#	'id': <job_id>,
		#}
		#get('job_specifications/run', params)
		path = f'job_specifications/run.xml'
		output = self.get(path, params=params)
		return output
	
	def config_revision_get(self, params):
		#params = {
		#	'DeviceID': <device_id>,
		#}
		#get('config_revisions/get_configs', params)
		path = f'config_revisions/get_configs.xml'
		output = self.get(path, params=params)
		return output
	
	def query(self, section, params={}):
		path = f'{section}/find.xml'
		output = self.get(path, params=params)
		return output
	
	def query_all(self, section, params={}):
		if not params:
			params = {
				'limit':	10000,
				'start':	0,
			}
		else:
			params['limit'] = 10000
			params['start'] = 0
		
		output = []
		query_raw = self.query(section, params=params)
		output.append(query_raw)
		
		all_result_lengths = [len(x['result'][section]) for x in output if x['success']]
		result_sum = sum(all_result_lengths)
		while result_sum % params['limit'] == 0:
			all_result_lengths = [len(x['result'][section]) for x in output if x['success']]
			result_sum = sum(all_result_lengths)
			params['start'] = result_sum
			query_raw = self.query(section, params=params)
			output.append(query_raw)
		return output
	
	def parse_xml_oldest(self, xml_raw):
		output = []
		et_raw = xml.fromstring(xml_raw.text)
		entries = list(et_raw[-1])
		if not entries:
			print('[E] nothing to parse')
			return ''
		for entry in list(entries):
			if not entry:
				continue
			else:
				info = {
					'collector_source':	xml_raw.url.split('/')[2],
				}
			for attribute in list(entry):
				if len(list(attribute)) > 0:
					info[attribute.tag] = {}
					for attribute_child in list(attribute):
						info[attribute.tag][attribute_child.tag] = attribute_child.text
				else:
					info[attribute.tag] = attribute.text
			output.append(info)
		return output
	
	def parse_xml_old(self, xml_root):
		output = {}
		parents = list(xml_root)
		for parent in list(parents):
			if len(list(parent)) > 0:
				output[parent.tag] = [
					self.parse_xml(child)
					for child in list(parent)
				]
			else:
				output[parent.tag] = parent.text
		return output
	
	def parse_xml(self, xml_root):
		output = {xml_root.tag: ''}
		children = list(xml_root)
		if children:
			# all children same
			if all(child.tag == children[0].tag for child in children):
				output = [
					self.parse_xml(child) for child in children
				]
			# different children
			else:
				output = {
					child.tag: self.parse_xml(child)
					for child in children
				}
		else:
			output = xml_root.text
		return output

if __name__ == '__main__':
	#na = NetMRI('custom')
	
	# unit test
	'''
	ida = na.query(
		'infra_devices',
		params={
			'DeviceName':'',
			'limit':5,
			'start':0,
			'methods':'running_config_text',
		}
	)
	'''
	# or all
	'''
	ida = na.query_all('infra_devices')
	if all([x['success'] for x in ida]):
		print('[I] Successful queries for all requests')
	else:
		print('[W] Some queries were not successful')
	results = [y for x in ida for y in x['result']]
	print(f'[I] Found {len(results)} results')
	'''
	print('[I] End')
