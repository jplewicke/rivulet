# Rivulet

Rivulet is a simple webservice that allows people to **pay** each other with **IOUs** and **promises**, _even if_ the people making a trade don't know or trust each other. If you want to pay a stranger, it searches both of your social **trust networks** for a sequence of **mutual acquaintances** to vouch for you by extension.

Rivulet is a simplified version of Ryan Fugger's [Ripple Monetary System](http://ripple-project.org).  It's intended to be plugged into existing websites, and doesn't support exchange rates, multiple units of account charging interest or demurrage, or ship with much of a user interface.

If you're looking for a simple way for your users to trade babysitting sessions, car rides, books or CDs, or even to replace money, you've found the right github repo.

## Benefits and Features

Rivulet allows website developers to quickly add a **digital payment** system for their users that is trustworthy.  Since users set whom they trust, they feel empowered.  

Rivulet is **hard for people to game**: doing sham transactions or setting up sock-puppets doesn't earn them any more trust from other users.

Rivulet is **spam-resistant**: even if 20,000 spammers set up accounts, they can't steal anything from legitimate users since they'll be disconnected from the main trust network.

Rivulet **scales well**: it can handle simultaneous requests, find trust paths between people with more than 6 degrees of separation, and handle trust networks with tens of thousands of participants.

Rivulet uses **ACID transactions**, so payments will either go through completely or not have any affect.  Simultaneous attempts to pay with the same IOUs won't end up causing double payments or corruption.

Rivulet is a **simple RESTful web service**, so it's easy to integrate with your existing website.  You can keep your existing interface and integrate Rivulet the way you want to. It's based on [OpenTransact](http://opentransact.org "OpenTransact"), the fledgling spec for simple financial transactions.

## Installation

So far, Rivulet has been successfully run on OS X and Ubuntu 10.10/10.4. It should also work well on Linux and on VPS hosting services like Amazon EC2 or Linode.

1. Install [JRuby](http://www.jruby.org/).  (You need this instead of regular Ruby since Rivulet uses the Java graph database [Neo4j](http://neo4j.org), and hence runs on the JVM. This also makes Rivulet unsuitable for running on Heroku.)

2. Download a copy of Rivulet to a working directory using git:
`git clone https://github.com/jplewicke/rivulet.git`

3. Install [bundler](http://gembundler.com/):
`sudo jruby -S gem install bundler`   If your version of rubygems is not up-to-date, you can run `sudo jruby -S gem update`.  You may need to follow the steps outlined [here](http://forums.aptana.com/viewtopic.php?t=7652) to update a really old version.

4. Change directories to the directory that Rivulet was downloaded into.

5. Install all of Rivulet's other dependencies:
`sudo jruby -S bundle install`

6. Set up some test data for Rivulet's test suite: `jruby -S bundle exec test_init.rb` .  This will create 500 users(User\_0 - User\_499) with random credit relationships.

7. Run the unit tests to make sure that most stuff is working on your system:
`jruby -S bundle exec test.rb`  .  Since the OpenTransact asset reservations aren't working completely, you should expect the last couple tests to fail.

8. Start the server:
`jruby -S bundle exec routes.rb`

9. Try Rivulet's client by opening up [http://localhost:4567/](http://localhost:4567/) in your web browser(only tested on Firefox so far).

## Using Rivulet

If you're trying to get Rivulet talking to another webapp, you'll probably want to reference either routes.rb or test.rb to see some examples of how to communicate with Rivulet from the command line.

## Updating Rivulet

You can update your copy of Rivulet's source code by running `git pull origin master`.  Since the Neo4j database schema isn't stable yet, you will want to avoid doing this for anything that modifies neo_classes.rb .  I'll be linking to a better guide to contributing patches and such with git as soon as I find one.

## License

Rivulet is available under the GNU Affero General Public License, as seen in the LICENSE file.  Briefly speaking, this means that if you modify this program, you have to make your changes available to anyone who interacts with it over a network. 

If you have a particular application that requires different licensing, please contact John Paul Lewicke at jplewicke@gmail.com .  Rivulet uses the graph database Neo4j, which charges licensing fees for use with closed source code.

The JQuery files in public/ contain their own licensing information.

## Acknowledgements

Thanks to Romualdo and Miles for testing Rivulet on their setups, and to Ryan for getting this whole crazy Ripple thing going in the first place.