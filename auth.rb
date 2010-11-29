require "sinatra"
require "neo_classes"

#Throws a 401 if the provided credentials don't match at least one of the enumerated users.
def protected!(user_ids)
  unless user_ids.any? {|user_id| authorized?(user_id) }
    response['WWW-Authenticate'] = %(Basic realm="You may have mistyped your username or password. You can either retype them here or hit ESC twice.")
    throw(:halt, [401, "Not authorized\n"])
  end
end

def authorized?(user_id)
  user_creds = User.creds_from_id(user_id)
  @auth ||=  Rack::Auth::Basic::Request.new(request.env)
  puts "user_id: #{user_id}"
  puts "auth.provided? #{@auth.provided?}"
  puts "auth.basic? #{@auth.basic?}"
  puts "auth.credentials[0]: #{@auth.credentials[0]}"
  puts "auth.credentials[1]: #{@auth.credentials[1]}"
  puts "user_creds[0]: #{user_creds}"
  #puts "user_creds[1]: #{user_creds[1]}"
  @auth.provided? && @auth.basic? && @auth.credentials && @auth.credentials == user_creds
end

def authed_user(user_ids)
  user = user_ids.detect {|uid| authorized?(uid)}
end
  