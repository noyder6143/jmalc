# Turn on student accounts (about 15 minutes, free)

Right now the apps save progress on each student's own device. These steps add
optional student accounts, cloud saving, and your teacher dashboard. Students who
never sign in keep using the apps exactly as before.

1. **Make a free Supabase account.** Go to https://supabase.com, click **Start your project**, and sign up (signing in with GitHub is fine).
2. **Create a project.** Click **New project**. Name it `digital-literacy`, make up a database password (save it somewhere), pick the region closest to you (East US), and keep the **Free** plan. Wait a minute or two while it sets up.
3. **Copy two values.** In the project, click **Connect** at the top (or **Project Settings > API Keys**). Copy the **Project URL** (looks like `https://abcd1234.supabase.co`) and the **anon public** key (a long code that starts with `eyJ` or `sb_publishable_`). Send both to your assistant. Never share the `service_role` or secret key.
4. **Create the tables.** In the left menu, open **SQL Editor**, click **New query**, paste everything in `schema.sql`, and click **Run**. You should see "Success. No rows returned."
5. **Turn off email confirmation.** Go to **Authentication > Sign In / Providers**. Under **User Signups**, switch **Confirm email** OFF and click **Save**. (Leave **Allow new users to sign up** ON.) Students can then sign up with any email, even one they can't check.
6. **Wait for the update.** Your assistant puts the two values into `config.js` and publishes it. Then a **☁️ Sign in** button shows up in both apps and on the class page.
7. **Pick a class code,** like `DL2026`. Students type it when they make an account, and it is how the dashboard knows they are in your class.
8. **Make your own account.** Open the class page, tap **☁️ Sign in > New account**, and enter your name, the class code, your email, and a password.
9. **Make yourself the teacher.** Back in the **SQL Editor**, run this one line with your email in it:
   ```sql
   update public.profiles set role = 'teacher' where id = (select id from auth.users where email = 'YOUR-EMAIL@example.com');
   ```
10. **Open your dashboard.** Go to the **Teacher** link at the bottom of the class page (`teacher.html`) and sign in. As students sign up with your class code, they show up there with their Quest XP, badges, best scores, and Final Exam Review results. Use **Download CSV** to export them.

**Good to know**
- The anon key is meant to be public, like a building's street address. Students can only read and change their own data, and only your teacher account can see your class. Row Level Security rules in `schema.sql` enforce this.
- Student forgot their password? In Supabase, go to **Authentication > Users**, find the student, and use the menu to delete them. They can sign up again, but their saved progress will be gone. (Turning off confirmation also turns off password-reset emails.)
- Wrong class code? Fix it in **Table Editor > profiles > class_code**.
- Free projects pause after about a week with no activity. If that happens, open the project in Supabase and click **Restore**. While it's paused, the apps keep saving on each device and sync again later.
