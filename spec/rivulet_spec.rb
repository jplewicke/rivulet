require File.dirname(__FILE__) + '/spec_helper'
 
describe "Routes" do
  include Rack::Test::Methods
  def app
      Sinatra::Application
    end
  
 
  it "should respond to /" do
    get '/'
    last_response.should be_ok
  end
end