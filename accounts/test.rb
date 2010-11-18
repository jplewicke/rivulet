ENV['RACK_ENV'] = 'test'

require 'routes'
require 'test/unit'
require 'rack/test'
require "base64"

class RoutesTest < Test::Unit::TestCase
  include Rack::Test::Methods
  def app
    Sinatra::Application
  end

  
  def test_without_authentication
    get '/accounts/User_133'
    assert_equal 401, last_response.status
  end

  def test_with_bad_credentials
    get '/accounts/User_145', {}, {'HTTP_AUTHORIZATION' => encode_credentials('go', 'away')}
    assert_equal 401, last_response.status
  end

  def test_with_proper_credentials
    #get '/accounts/User_133', {}, {'HTTP_AUTHORIZATION'=> encode_credentials('User_133', 'pw')}
    get '/accounts/User_133', {}, cred(133)
    assert_equal 200, last_response.status
  end
  
  def test_acct_creation
    post '/accounts', {:user => "User_#{rand(7000)+1000}", :secret => "pw"}, {}
    assert_equal 200, last_response.status
  end
  
  def test_acct_noncreation
    post '/accounts', {:user => "User_200", :secret => "pw"}, {}
    assert_equal 403, last_response.status
  end
  
  def test_credit_extension_parsefailure
    post '/credits/User_133', {:to => "User_134", :amount => "dinosaur"}, cred(133)
    assert_equal 400, last_response.status
  end
  
  def test_credit_extension_auth_failure
    post '/credits/User_133', {:to => "User_134", :amount => 5.4}, cred(167)
    assert_equal 401, last_response.status
  end

  def test_credit_extension
    post '/credits/User_133', {:to => "User_134", :amount => 5.4}, cred(133)
    assert_equal 200, last_response.status
  end
  
  private

  def encode_credentials(username, password)
    "Basic " + Base64.encode64("#{username}:#{password}")
  end
  
  def cred(uid)
    return {'HTTP_AUTHORIZATION'=> encode_credentials("User_#{uid}", 'pw')}
  end
end