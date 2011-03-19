require File.dirname(__FILE__) + '/spec_helper'
 
describe "Routes" do
  include Rack::Test::Methods
  def app
      Sinatra::Application
    end
  
    it "should require authentication to view user info" do
      get '/accounts/User_133'
      last_response.status.should == 401
    end
 
  it "should respond to /" do
    get '/'
    last_response.should be_ok
  end
  
  #SUBHERE
  
  private

  def encode_credentials(username, password)
    "Basic " + Base64.encode64("#{username}:#{password}")
  end
  
  def cred(uid)
    return {'HTTP_AUTHORIZATION'=> encode_credentials("User_#{uid}", 'pw')}
  end
  
  def bad_cred
    {'HTTP_AUTHORIZATION'=> encode_credentials("go", 'away')}
  end
end

