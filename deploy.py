#! /usr/bin/env python

import locale, yaml, os, json, time, collections
from dialog import Dialog

config_file="instances.yaml"
if not os.path.exists(config_file):
    with open(config_file, 'w'): pass
with open(config_file, 'r') as stream:
    config_data = yaml.load(stream)
print config_data

locale.setlocale(locale.LC_ALL, '')

d = Dialog(dialog="dialog")
d.set_background_title("Contrail Deployer")

class Instance(object):
  def __init__(self, provider, name=None, instance_data=None):
    self.provider = provider
    self.config_file="instances_" + self.provider + ".yaml"
    if instance_data:
      self.instance_data = instance_data
      self.name = name
      self.config = self.instance_data
    else:
      self.name = ''
      self.config = {}
  def save(self):
    if not os.path.exists(self.config_file):
      with open(self.config_file, 'w'): pass
    with open(self.config_file, 'r') as stream:
      self.config_data = yaml.load(stream)
    if self.config_data['instances'] == None:
      self.config_data['instances'] = {}
    self.config_data['instances'][self.name] = self.config
    with open(self.config_file, 'w') as outfile:
      yaml.safe_dump(self.config_data, outfile, default_flow_style=False)
    d.infobox("Saving...", width=40,
              title="Exiting")
    time.sleep(1)
    list_instances(self.provider)
  def list(self):
    if not self.instance_list:
      code = d.yesno("No Instances configured, add one?")
      if code == "ok":
        self.add()
      if code == "cancel":
        provider_action_menu(self.provider)  
    choices_list = []
    instance_counter = 1
    for instance in self.instance_list:
       choices_list.append((str(instance_counter), instance)) 
    code, tag = d.menu("Instances List",
                   choices = choices_list,
                            cancel_label = "Back")
    pass
  def configure(self):
    if len(self.config) == 0:
      if self.provider == 'aws':
        self.config['vpc_subnet_id'] = ''
      self.config['other_config'] = ''
    od = collections.OrderedDict(sorted(self.config.items()))
    config_element_list = [('name',
                            1,
                            1,
                            self.name,
                            1,
                            20,
                            20,
                            20)]
    config_element_count = 2
    for key, value in od.iteritems():
      if key != 'roles':
        config_element_list.append((key,
                                  config_element_count,
                                  1,
                                  value,
                                  config_element_count,
                                  20,
                                  20,
                                  20))
        config_element_count = config_element_count + 1
    code, fields = d.form("Instance configuration",
                          config_element_list,
                          ok_label = "Save",
                          cancel_label = "Back",
                          extra_button = True,
                          extra_label = "Configure Roles",
                          width=77)
    if code == "cancel":
      list_instances(self.provider)
    self.name = fields[0]
    config_element_count = 1
    for key, value in od.iteritems():
      if key != 'roles':
        self.config[key] = fields[config_element_count]
        config_element_count = config_element_count + 1
    if code == "extra":
      self.configure_roles()
    if code == d.DIALOG_OK:
      self.save()
  def configure_roles(self):
      choices_list = []
      roles_dict = collections.OrderedDict()
      roles_dict['config_database'] = ''
      roles_dict['config'] = ''
      roles_dict['control'] = ''
      roles_dict['analytics_database'] = ''
      roles_dict['analytics'] = ''
      roles_dict['webui'] = ''
      roles_dict['k8s_master'] = ''
      roles_dict['vrouter'] = ''
      roles_dict['k8s_node'] = ''
      if not 'roles' in self.config:
        self.config['roles'] = {}
      for role in roles_dict:
        if role in self.config['roles']:
          roles_dict[role] = True
        else:
          roles_dict[role] = False
      for key, value in roles_dict.iteritems():
        choices_list.append((key,"",value))
      code, roles  = d.checklist("Select Roles",
                                 list_height = 20,
                                 height = 20,
                                 choices = choices_list)
      if code == "ok":
        self.config['roles'] = {}
        for role in roles:
          self.config['roles'][role] = ''
        self.configure()
      if code == "cancel":
        self.configure()
   
class Provider(object):
  def __init__(self, provider):
    self.provider = provider
    self.config_file="instances_" + self.provider + ".yaml"
    if not os.path.exists(self.config_file):
      with open(self.config_file, 'w'): pass
    with open(self.config_file, 'r') as stream:
      self.config_data = yaml.load(stream)
    self.provider_list = self.config_data['provider_config']
  def show(self):
    provider_data = self.provider_list[self.provider]
    config_element_list = []
    config_element_count = 1
    for config_element in provider_data:
      if provider_data[config_element] == None:
        provider_data[config_element] = ""
      config_element_list.append((config_element,
                                  config_element_count,
                                  2,
                                  str(provider_data[config_element]),
                                  config_element_count,
                                  30,
                                  30,
                                  30))
      config_element_count = config_element_count + 1
    print config_element_list
    code, fields = d.form(self.provider + " configuration",
                          config_element_list,
                          ok_label = "Save",
                          cancel_label = "Back",
                          width=77)
    config_element_count = 0
    for config_element in fields:
      provider_data[config_element_list[config_element_count][0]] = \
        config_element 
      config_element_count = config_element_count + 1
    with open(self.config_file, 'w') as outfile:
      yaml.safe_dump(self.config_data, outfile, default_flow_style=False)
    if code == d.DIALOG_OK:
      d.infobox("Saving...", width=40,
                title="Exiting")
      time.sleep(1)
      self.show()
    elif code == d.DIALOG_CANCEL:
      provider_action_menu(self.provider)
    pass
  def add(self):
    pass
  def delete(self):
    pass
  def edit(self):
    pass

def save(provider, data):
    config_file="instances_" + provider + ".yaml"
    if not os.path.exists(config_file):
      with open(config_file, 'w'): pass
    with open(config_file, 'r') as stream:
      config_data = yaml.load(stream)
    with open(config_file, 'w') as outfile:
      yaml.safe_dump(config_data, outfile, default_flow_style=False)

def provider_selection_menu():
    code, tag = d.menu("Provider List",
                   choices=[("1", "AWS"),
                            ("2", "GCE"),
                            ("3", "KVM"),
                            ("3", "BMS")],
                            cancel_label = "Back")
    if code == d.DIALOG_OK:
        if tag == "1":
          provider_action_menu("aws")
        if tag == "2":
          provider_obj.show('gce')
        pass
    elif code == d.DIALOG_CANCEL:
      main()

def provider_action_menu(provider):
    code, tag = d.menu("Action List",
                   choices=[("1", "Configure Provider"),
                            ("2", "Configure Instances"),
                            ("3", "Configure Contrail"),
                            ("4", "Configure Kolla")],
                            cancel_label = "Back")
    if code == d.DIALOG_OK:
        if tag == "1":
          provider_obj = Provider(provider)
          provider_obj.show()
        if tag == "2":
          list_instances(provider)
          #instance_obj = Instance(provider)
          #instance_obj.list()
        pass
    elif code == d.DIALOG_CANCEL:
      provider_selection_menu()

def list_instances(provider):
    config_file="instances_" + provider + ".yaml"
    if not os.path.exists(config_file):
      with open(config_file, 'w'): pass
    with open(config_file, 'r') as stream:
      config_data = yaml.load(stream)
    instance_list = config_data['instances']
    if not instance_list:
      code = d.yesno("No Instances configured, add one?")
      if code == "ok":
        instance_obj = Instance(provider)
        instance_obj.configure()
      if code == "cancel":
        provider_action_menu(provider)
    else:
      choices_list = []
      instance_count = 1
      for instance in instance_list:
        choices_list.append((instance, ""))
        instance_count = instance_count + 1
      print choices_list
      code, tag = d.menu("Instance List",
                         choices=choices_list,
                         cancel_label = "Delete",
                         help_button = True,
                         help_label = "Back",
                         extra_button = True,
                         extra_label = "Add")
      print "tag %s" %tag
      if code == "ok":
        instance_obj = Instance(provider, tag, instance_list[tag])
        instance_obj.configure()
      if code == "extra":
        instance_obj = Instance(provider)
        instance_obj.configure()
      if code == "help":
        provider_action_menu(provider)
      if code == "cancel":
        print tag
        del instance_list[tag]
        list_instances(provider)

def main():
    # We could put non-empty items here (not only the tag for each entry)
    code, tag = d.menu("Main Menu",
                   choices=[("1", "Configuration"),
                            ("2", "Execution")])
    if code == d.DIALOG_OK:
      if tag == "1":
        provider_selection_menu()
      if tag == "2":
        instance_obj = Instance()
      pass

main()
