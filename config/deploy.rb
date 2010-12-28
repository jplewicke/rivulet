#default_run_options[:pty] = true

#Relies on :password and :aws_private_key_path being set in the deployer .caprc file.

set :application, "rivulet"
set :repository,  "https://github.com/jplewicke/rivulet"

# If you aren't deploying to /u/apps/#{application} on the target
# servers (which is the default), you can specify the actual location
# via the :deploy_to variable:
set :deploy_to, "/home/deploy/#{application}"
set :repository, "/Users/jplewicke/Dropbox/rivulet"
set :scm, "git"
set :deploy_via, :copy

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

set :context_root, "/"

set :jruby_location, "/home/deploy/jruby/"

set :gf_port, "80"

set :environment, "production"

set :jruby_runtimes, "1"

set :jruby_min_runtimes, "1"

set :jruby_max_runtimes, "1"


default_run_options[:pty] = true


namespace :ec2 do
  
  set :new_user, "deploy"
  
  set :superuser, "ubuntu"
  
  desc "Spin up a new Rivulet server on EC2"
  task :add_server do
    create_ec2_server
    wait_spinup
    bootstrap_deploy_user
    setup_env
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
    sleep 30.0
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
    puts default_environment
    puts default_environment[:PATH]
    run "echo $PATH"
    update_apt_get
    install_dev_tools
    install_git
    install_subversion
    install_jruby
    download_rivulet
    install_gems
    run_install_test
    launch_rivulet
  end

  desc "Update apt-get sources"
  task :update_apt_get do
    run "#{sudo} apt-get update -y"
  end

  desc "Install Development Tools"
  task :install_dev_tools do
    run "#{sudo} apt-get install build-essential -y"
    run "#{sudo} apt-get install gawk -y"
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
    run "#{sudo} apt-get install openjdk-6-jre-headless -y"
    run "wget http://jruby.org.s3.amazonaws.com/downloads/1.5.6/jruby-bin-1.5.6.tar.gz"
    run "md5sum jruby-bin-1.5.6.tar.gz  | awk '$1 !~ /94033a36517645b7a7ec781a3507c654/ {print \"bad jruby tar\" ; exit 1}'"
    run "tar xvzf jruby-bin-1.5.6.tar.gz"
    run "rm -f jruby-bin-1.5.6.tar.gz"
    run "mv jruby-1.5.6 jruby"
    
    #Setup JRUBY environment information.  Need to have the right path for deploy user,
    #sudoing, and any other users.
    
    run "echo export JRUBY_HOME=`pwd`/jruby >> ~/.bashrc"
    run "echo 'export PATH=$PATH:$JRUBY_HOME/bin' >> ~/.bashrc"
    run "echo 'alias sudo=\"sudo env PATH=$PATH\"' >> ~/.bashrc"
    run "#{sudo} chmod o+w /etc/environment"
    run "echo JRUBY_HOME=\"`pwd`/jruby\" >> /etc/environment"
    run "echo PATH=\"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:`pwd`/jruby/bin\" >> /etc/environment"
    run "echo \"echo Defaults   secure_path=\"/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:`pwd`/jruby/bin\" >> /etc/sudoers\" | sudo su"
    run "#{sudo} chmod o-w /etc/environment"
    
    #Add to /etc/environment/?
    
    #default_environment[:PATH] = '/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/home/deploy/jruby/bin'
    #default_environment[:JRUBY_HOME] = '/home/deploy/jruby'
    
    teardown_connections_to(sessions.keys)
  end
  
  desc "Clone the Rivulet repository from Github."
  task :download_rivulet do
    run "git clone https://github.com/jplewicke/rivulet.git"
  end
  
  desc "Download gems and Rivulet dependencies"
  task :install_gems do
    run "#{sudo} jruby -S gem install bundler"
    run "cd rivulet ; ls -altr"
    run "cd rivulet ; #{sudo} jruby -S bundle install"
  end
  
  desc "Check that the Rivulet installation is working well."
  task :run_install_test do
    run "cd rivulet ; jruby -S bundle exec test_init.rb"
    run "cd rivulet ; jruby -S bundle exec test.rb"
  end
  
  desc "Launch the Rivulet website."
  task :launch_rivulet do
    run "cd rivulet ; sudo nohup jruby -S bundle exec glassfish -p 80 > log.log 2>&1 &"
    puts "Rivulet is now running at http://#{hostname} ."
    puts "You can access this server by running \" ssh deploy@#{hostname} \"."
  end    
end  
