#default_run_options[:pty] = true

#Relies on :password and :aws_private_key_path being set in the deployer .caprc file.

set :application, "rivulet"
set :repository,  "https://github.com/jplewicke/rivulet"

# If you aren't deploying to /u/apps/#{application} on the target
# servers (which is the default), you can specify the actual location
# via the :deploy_to variable:
set :deploy_to, "/var/www/#{application}"

# If you aren't using Subversion to manage your source code, specify
# your SCM below:
set :scm, :git

#role :app, "www.tryrivulet.com"
#role :web, "www.tryrivulet.com"
#role :db,  "www.tryrivulet.com", :primary => true

#set :application, "yyyyy.vamosa.com"
#set :domain, "yyyyy.vamosa.com"
set :ami_name, "ami-c9bc58a0"

#change to alestic maverick
set :ami_name, "ami-1a837773" 
#change to alestic lucid
#set :ami_name, "ami-a403f7cd"
set :image_type, "m1.small"



default_run_options[:pty] = true


namespace :ec2 do
  
  set :new_user, "deploy"
  
  set :superuser, "ubuntu"
  
  desc "Setup server"
  task :setup_server do
    create_ec2_server
    wait_spinup
    bootstrap_deploy_user
    #setup_env
    #shutdown_ami
    #test_sudo
  end
  
  desc "sudo_testing"
  task :test_sudo do
    #set :user, "ubuntu"
    
    #ssh_options[:keys] = aws_private_key_path
    puts user
    
    run "pwd"
    
    #run "ls -altr /home/ubuntu/.ssh"
    run "#{sudo} ls -altr /home/ubuntu/.ssh"
    
    #run "apt-get update -y"
    run "#{sudo} apt-get update -y"
  end
  
  desc "spinup a server"
  task :create_ec2_server do
    set :ami, `ec2-run-instances -k #{aws_private_key_name} -t #{image_type} #{ami_name} | awk '$1 ~ /INSTANCE/ {printf $2}'`
    puts ami
  end
  
  desc "wait for server to spinup and grab the host-name"
  task :wait_spinup do
    set :hostname, "pending"
    dly = 5.0
    
    while hostname == "pending" do
      sleep dly 
      set :hostname, `ec2-describe-instances #{ami} | awk '$1 ~ /INST/ {printf $4}'`
      dly *= 1.5
    end
    server hostname, :web, :app, :db
    puts hostname
  end
  
  desc "uploads id_rsa.pub to the EC2 instance's deploy users authorized_keys2 file"
  task :bootstrap_deploy_user do
    
    default_run_options[:pty] = false
    sleep 10.0
    set :user, superuser
    
    ssh_creds = "-i #{aws_private_key_path} #{superuser}@#{hostname} \"sudo "
    
    #Add server to known hosts.
    system "ssh -oStrictHostKeyChecking=no #{ssh_creds} pwd\""
    
    system "ssh #{ssh_creds} groupadd admin\""
    system "ssh #{ssh_creds} useradd -d /home/#{new_user} -s /bin/bash -m #{new_user}\""
    system "ssh #{ssh_creds} echo #{new_user}:#{password} | sudo chpasswd\""
    system "ssh #{ssh_creds} usermod -a -G admin #{new_user}\""
    
    system "ssh #{ssh_creds} mkdir /home/#{new_user}/.ssh\""
    for key in ssh_options[:keys]
      # Run this command in a subshell so we can sudo for it.
      system "cat  #{key}.pub | ssh #{ssh_creds} sh -c \'cat >> /home/#{new_user}/.ssh/authorized_keys\'\""
    end
    system "ssh #{ssh_creds} chmod -R go-rwx /home/#{new_user}/.ssh\""    
    system "ssh #{ssh_creds} chown -R #{new_user}:#{new_user} /home/#{new_user}/.ssh\""
    #system "scp -i #{aws_private_key_path} config/deploy_sudoers #{superuser}@#{hostname}:/etc/sudoers"
    
    set :user, new_user
    default_run_options[:pty] = true
  end
  
  task :shutdown_ami do
    system "ec2-terminate-instances #{ami}"
  end
  
  desc "Setup Environment"
  task :setup_env do
    update_apt_get
    install_dev_tools
    install_git
    install_subversion
  end

  desc "Update apt-get sources"
  task :update_apt_get do
    run "#{sudo} apt-get update -y"
  end

  desc "Install Development Tools"
  task :install_dev_tools do
    run "#{sudo} apt-get install build-essential -y"
  end

  desc "Install Git"
  task :install_git do
    run "#{sudo} apt-get install git-core git-svn -y"
  end

  desc "Install Subversion"
  task :install_subversion do
    run "#{sudo} apt-get install subversion -y"
  end
  
  desc "Install JRuby"
  task :install_jruby do
    run "#{sudo} apt-get update"
  end
end  