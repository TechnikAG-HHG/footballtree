    def save_team_names_in_db(self):
        name_entries = self.name_entries

        # Get existing teams from the database
        self.cursor.execute("SELECT id, teamName, mp3Path FROM teamData")
        existing_teams = {row[1]: (row[0], row[2]) for row in self.cursor.fetchall()}
        
        team_ids_to_delete = []

        # Delete teams not in the entries and reassign IDs
        teams_to_delete = set(existing_teams.keys()) - {entry.get().strip() for entry in name_entries}
        for team_name in teams_to_delete:
            team_id, _ = existing_teams[team_name]
            self.cursor.execute("DELETE FROM teamData WHERE id = ?", (team_id,))
            team_ids_to_delete.append(team_id)
            

        # Update existing teams and add new teams with default values
        for i, entry in enumerate(name_entries):
            team_name = entry.get().strip()
            team_id1 = i + 1
            mp3_path = self.mp3_list.get(i)

            if team_name != "":
                # Update existing team
                if team_name in existing_teams:
                    team_id, existing_mp3_path = existing_teams[team_name]
                    if existing_mp3_path != mp3_path:
                        # Update MP3 path for existing team
                        if mp3_path is not None:
                            self.cursor.execute("UPDATE teamData SET mp3Path = ? WHERE id = ?", (mp3_path, team_id))
                else:
                    # Add new team with default values
                    try:
                        #print("team_id1", team_id1, "team_ids_to_delete", team_ids_to_delete)
                        if team_id1 in team_ids_to_delete:
                            if mp3_path is not None:
                                self.cursor.execute("UPDATE teamData SET teamName = ?, mp3Path = ? WHERE id = ?", (team_name, mp3_path, team_id1))
                                existing_teams[team_name] = (self.cursor.lastrowid, mp3_path)
                            else:
                                self.cursor.execute("UPDATE teamData SET teamName = ? WHERE id = ?", (team_name, team_id1))
                                existing_teams[team_name] = (self.cursor.lastrowid, None)
                                team_ids_to_delete.remove(team_id1)
                        else:
                            if mp3_path is not None:
                                self.cursor.execute("INSERT INTO teamData (teamName, goals, mp3Path) VALUES (?, 0, ?)", (team_name, mp3_path))
                                existing_teams[team_name] = (self.cursor.lastrowid, mp3_path)
                            else:
                                self.cursor.execute("INSERT INTO teamData (teamName, goals) VALUES (?, 0)", (team_name,))
                                existing_teams[team_name] = (self.cursor.lastrowid, None)
                            
                    except sqlite3.IntegrityError:
                        for i in range(1, 100):
                            new_team_name = f"{team_name} {i}"
                            if new_team_name not in existing_teams:
                                team_name = new_team_name
                                break
                            
                        if team_id1 in team_ids_to_delete:
                            if mp3_path is not None:
                                self.cursor.execute("UPDATE teamData SET teamName = ?, mp3Path = ? WHERE id = ?", (team_name, mp3_path, team_id1))
                                existing_teams[team_name] = (self.cursor.lastrowid, mp3_path)
                            else:
                                self.cursor.execute("UPDATE teamData SET teamName = ? WHERE id = ?", (team_name, team_id1))
                                existing_teams[team_name] = (self.cursor.lastrowid, None)
                            team_ids_to_delete.remove(team_id1)
                        
                        else:
                            if mp3_path is not None:
                                self.cursor.execute("INSERT INTO teamData (teamName, goals, mp3Path) VALUES (?, 0, ?)", (team_name, mp3_path))
                                existing_teams[team_name] = (self.cursor.lastrowid, mp3_path)
                            else:
                                self.cursor.execute("INSERT INTO teamData (teamName, goals) VALUES (?, 0)", (team_name,))
                                existing_teams[team_name] = (self.cursor.lastrowid, None)

        #for team_id in team_ids_to_delete:
        #    self.cursor.execute("DELETE FROM teamData WHERE id = ?", (team_id,))
        
        # get all ids from teamData
        self.cursor.execute("SELECT id FROM teamData")
        team_ids = [row[0] for row in self.cursor.fetchall()]
        #team_ids.sort()
        for i, team_id in enumerate(team_ids):
            if i + 1 != team_id:
                print("i+1", i+1, "team_id", team_id, "team_ids", team_ids, "team_ids_to_delete", team_ids_to_delete)
                self.cursor.execute("UPDATE teamData SET id = ? WHERE id = ?", (i+1, team_id))
        
        # Reassign IDs consecutively
        self.cursor.execute("DELETE FROM teamData WHERE id NOT IN (SELECT id FROM teamData ORDER BY id)")
        #self.cursor.execute("UPDATE SQLITE_SEQUENCE SET seq = (SELECT MAX(id) FROM teamData)")

        #print("tests")

        team_names = self.read_teamNames()
        team_names.pop(0)

        self.updated_data.update({"Teams": team_names})
        self.connection.commit()