# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant::Config.run do |config|
  #config.vm.box = "trusty-server-cloudimg-amd64-vagrant-disk1"
  #config.vm.box_url = "https://cloud-images.ubuntu.com/vagrant/trusty/current/trusty-server-cloudimg-amd64-vagrant-disk1.box"
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  config.vm.share_folder "v-app", "/usr/local/src/madrona", "./"
  config.vm.provision :shell, :path => "utils/provision.sh"
  config.vm.forward_port 8888, 8888
  config.vm.customize ["modifyvm", :id, "--cpus", 2]
  config.vm.customize ["modifyvm", :id, "--memory", 1280]
end
