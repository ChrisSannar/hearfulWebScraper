db.createUser(
  {
    user : "username",
    pwd : "password",
    roles : [
      {
        role : "readWrite",
        db  : "amazon-scraper-db"
      }
    ]
  }
)