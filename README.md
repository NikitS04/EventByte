# README and VIDEO

Your _readme_ goes here
I have included the video as the demo.mp4 but there may be no audio, if this is the case I have included subtitles in the video to show what I was explaining throughout the video.

Currently the database is empty, therefore first user created will become the superuser and this cant be changed. All users that you require will have to go through the registering process.

A user login and registration system, it works in a way such that the first user to register wil be the superuser. Every user that registers after will be a normal attendee. Invalid logins are checked for.
When registering, the password create must be at least a length of 8 characters, this is to reduce the chance of a hacker being able to brute-force an users password.
This is also true for when changing the password either when logged in or resetting the password via email link.

The super user will be able to:
Add events (with a event name, date, length in minutes (upto a max of 12 hours), capacity, location)
Cancel Event (Send an email to all attendees with tickets to notify them that the evet no longer exists)
Modify Capacity (Upto a maximum of 10,0000 users)
View Events
View Cancelled Events
View Transaction Log (User Registration, Ticket Allocation, Ticket Cancellation, Event Creation, Event Deletion, Password Changes, )
Be notfied (email) when the remaining capacity is less than 5% for a given event
Reset password from login page (forgot password via email link)
Change password when logged in
NOT get tickets as they are the superuser


The attendee will be able to:
View Events
View Cancelled Events
Get Tickets (up to a maximum of 5 per attendee) (sent an email for each ticket)
View Tickets (shows all the required details including barcode found by clicking 'view your barcode here' link)
Cancel Ticket (sends an email confirm their cancellation)
View number of tickets remaining (when remaining capacity is at less thean 5%)
Reset password from login page (forgot password via email link)
Change password when logged in

The guest user will be able to:
View Events
View Cancelled Events
View number of tickets remaining (when remaining capacity is at less thean 5%)
Register an account (to become an attendee)

Additional Features to be Marked:
1 Allows a user to get multiple tickets, upto a maximum of 5 tickets per user per event. At this point (5 tickets for the event for user) the get_ticket button dissapears and user can't get more tickets unless they cancel a ticket that they already have, in which case (now they have 4 tickets) they can get another ticket for the event.

2 Superusers and attendees can change their password using the 'settings' tab, where they enter their current password and then a new password (with repeat new password) to change their password. A suitable error message shows if the user didnt enter the information correctly.

The website follows a purple neon theme and all pages (once logged in) uses a navbar to navigate between pages. with the homepage containing some brief information about the website and contains an image carousel showcasing some highlights from past events



Your _video_ must replace the `demo.mp4` file in this folder
I have included the video as the demo.mp4 but there may be no audio, if this is the case I have included subtitles in the video to show what I was explaining throughout the video.

Before submitting your coursework, run `./clean.sh` as this will remove the virtual environment which can be reconstructed locally.

