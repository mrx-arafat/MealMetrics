# SSH Key Setup for GitHub - MealMetrics

## ✅ Your SSH Public Key

Copy this entire key (including `ssh-rsa` at the beginning):

```
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQDd1JoZtVt/kpODdcfqQHtdZRvFhoGMjxS7qqw/jxAtwgNdagIhURuqXaSLxDumEw5W/23N2f6814pt8g6XZ70qzKDd+33sLee8FSIfjsOUv1pkOZiKuicUGRiAaMkbUkctC4JzZTHPLG/1Q4yfqaCex357YuYt6KY4Uvvau8ET/lLDgyeR9caM4kuzxesK+E9m4FjAyyEP8iWoO1v8nsDY/HRJ0yoxlHJmbLwR5UpT/7758r3RmWq2zAzJwAkC+deHjMtnH3S3FbkjqPcqsy4cUU6c3VESYmvJ/KLpOGRivCbFnk6mlll9MujYbhgz17b4LNk5g9P3iVkbSR+gdCxwYlknWC7dhU3Iw5ktJ8PklZUWJiIsqP+O074xxIQSy7Cs9fxsLeUgG4OdseHqPEDrJlyGuXeBftpfMFnKvrjX+mzv3fkvCR3r1vuprCXAKv1buIctfb1p3u0ucJmLF4hamOJ6v3bcQKEuaRJRghuEBwswLOYgsrYaxCQrb5ADMsU= root@arafat-sf
```

---

## 🔐 Add SSH Key to GitHub

### Step 1: Copy the SSH Key Above

Select and copy the entire SSH key (from `ssh-rsa` to `root@arafat-sf`)

### Step 2: Go to GitHub SSH Settings

Visit: **https://github.com/settings/keys**

Or navigate:
1. Go to GitHub.com
2. Click your profile picture (top right)
3. Click **Settings**
4. Click **SSH and GPG keys** (left sidebar)

### Step 3: Add New SSH Key

1. Click **"New SSH key"** (green button)
2. **Title:** `MealMetrics VPS Server` (or any name you prefer)
3. **Key type:** `Authentication Key`
4. **Key:** Paste your SSH public key (the entire key from above)
5. Click **"Add SSH key"**
6. Confirm with your GitHub password if prompted

---

## 🔄 Change Git Remote to SSH

After adding the SSH key to GitHub, run these commands:

```bash
cd /var/www/MealMetrics

# Change remote URL from HTTPS to SSH
git remote set-url origin git@github.com:mrx-arafat/MealMetrics.git

# Verify the change
git remote -v
```

You should see:
```
origin  git@github.com:mrx-arafat/MealMetrics.git (fetch)
origin  git@github.com:mrx-arafat/MealMetrics.git (push)
```

---

## 🚀 Push to GitHub

Now you can push without any password:

```bash
# Push to GitHub
git push origin master
```

**First time only:** You'll see a message like:
```
The authenticity of host 'github.com' can't be established.
Are you sure you want to continue connecting (yes/no)?
```
Type: `yes` and press Enter

---

## ✅ Test SSH Connection

Before pushing, you can test the SSH connection:

```bash
ssh -T git@github.com
```

You should see:
```
Hi mrx-arafat! You've successfully authenticated, but GitHub does not provide shell access.
```

---

## 📋 Summary

1. ✅ SSH key already exists on your VPS
2. ⏳ Copy the SSH public key (shown above)
3. ⏳ Add it to GitHub: https://github.com/settings/keys
4. ⏳ Change git remote to SSH
5. ⏳ Push to GitHub

---

## 🆘 Troubleshooting

### "Permission denied (publickey)"
- Make sure you added the SSH key to GitHub
- Verify you copied the entire key including `ssh-rsa` at the start
- Check you're using the SSH URL: `git@github.com:mrx-arafat/MealMetrics.git`

### "Host key verification failed"
```bash
# Remove old GitHub host key
ssh-keygen -R github.com

# Try connecting again
ssh -T git@github.com
```

### Check SSH Key Permissions
```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

---

## 💡 Advantages of SSH

- ✅ No need to enter password/token every time
- ✅ More secure than HTTPS with tokens
- ✅ Works seamlessly with git commands
- ✅ No token expiration issues
- ✅ Industry standard for server authentication

---

**Ready?** Copy the SSH key above and add it to GitHub, then run the commands to push!

