
require 'rspec/core/rake_task'


namespace :spec do
  
  desc "Run core specs."
  RSpec::Core::RakeTask.new(:core) do |spec|
    spec.pattern = 'spec/*_spec.rb'
    spec.rspec_opts = ['--backtrace']
  end
end
task :spec => ['spec:core']