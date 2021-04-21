myguild_id = 721318863433629707  # guild id

footer = "Skyblock Services"  # footer for embeds
guild_name = "Skyblock Services"  # name of the guild
transcript_channel = 801908044287836200  # the channel to post transcripts to
ticket_inactivity_close_time = 345600  # in seconds
# role id of the general role given to experts
expert_role_id = 784539526944260116
when_to_update_database = 21600  # make sure that the `Tickets` database is upto date, while it shouldn't lack behind, any exceptions can cause ghost tickets or ticket with their owners left the server

# giving special access for the bot to some users, like the dev
access_privilage = ["640773439115886642"]

#the prefix of the bot
prefix = "<"

#a list of roles to give on verifying with ign
verified_role = []
#reaction to make the ticket with
ticket_reaction = "✉"
#msg sent when timeout
timeout_msg = "Ok I guess you changed your mind <:cat_juice:809248678140575745>"
#reaction to close a ticket
close_reaction = "🔒"
#reaction to open a closed ticket
open_reaction = "🔓"
#reaction to claim a ticket
claim_reaction = "📌"
#reaction to delete a ticket
delete_reaction = "🗑"
#pricing of each skill for the pet calc
pricing = {
    "combat": 1.9,
    "mining": 1.8,
    "farming": 1.7,
    "foraging": 1.4,
    "alchemy": 0.6,
    "fishing": 2.0
}
#default msg sent when a ticket is created, you can set a custom one in a panel, this is a default
default_ticket_msg = "Welcome, someone will attend you shortly\nPlease be sure to ask for collateral **if** applicable"
#default color of embeds
default_embed_color=0xF7CB0F
closed_category=761360591066497054

ticket_experts_id={"Pet Leveling":721688814103560242,
"Item Leveling":721688890557333594,
"Medal Shop":775264902863781910,
"Hoe Upgrading":782778422841704448,
"Enchanting":721689023856377917,
"Enchant Upgrading":785974880368590859,
"Dungeon Carrying":763829584260628500,
"Slayers":721689521556815883,
"Runecrafting":806293717148368987,
"Runecrafting EXP":806307295587598346}


bot_name="SkyTicket Services"
discord_embed="https://discord.com/widget?id=721318863433629707&theme=dark"