#Importing the libraries
import pandas as pd
import sqlite3
import sqlalchemy

# creating file path
dbfile = 'C:/Users/Dell/Desktop/Yash/Machine Learning/Db-IMDB.db'
# Create a SQL connection to our SQLite database
try:
    conn = sqlite3.connect(dbfile)    
except Error as e:
    print(e)

#Now in order to read in pandas dataframe we need to know table name
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(f"Table Name : {cursor.fetchall()}")

# Movie = pd.read_sql_query('SELECT * FROM Movie', conn)
# Person = pd.read_sql_query('SELECT * FROM Person', conn)
# Genre = pd.read_sql_query('SELECT * FROM Genre', conn)
# Language = pd.read_sql_query('SELECT * FROM Language', conn)
# Country = pd.read_sql_query('SELECT * FROM Country', conn)
# Location = pd.read_sql_query('SELECT * FROM Location', conn)
# M_Location = pd.read_sql_query('SELECT * FROM M_Location', conn)
# M_Country = pd.read_sql_query('SELECT * FROM M_Country', conn)
# M_Language = pd.read_sql_query('SELECT * FROM M_Language', conn)
# M_Genre = pd.read_sql_query('SELECT * FROM M_Genre', conn)
# M_Producer = pd.read_sql_query('SELECT * FROM M_Producer', conn)
# M_Director = pd.read_sql_query('SELECT * FROM M_Director', conn)
# M_Cast = pd.read_sql_query('SELECT * FROM M_Cast', conn)

# Question 1
# List all the directors who directed a 'Comedy' movie in a leap year. (You need to check that the genre is 'Comedy’ and year is a leap year) 
# Your query should return director name, the movie name, and the year.
Director_info = pd.read_sql_query("""
                                    SELECT Name FROM Person
                                    WHERE PID IN 
                                    (SELECT DISTINCT(PID) FROM M_Director 
                                    WHERE MID IN 
                                    (SELECT MID FROM Movie
                                    WHERE (year%4=0) AND (year%100!=0) OR (year%400=0) AND MID IN
                                    (SELECT MID FROM M_Genre 
                                    WHERE GID IN 
                                    (SELECT GID FROM Genre 
                                    WHERE Name LIKE '%Comedy%')))) 
                                    """, conn)

Movie_info = pd.read_sql_query("""
                                    SELECT title, year FROM Movie
                                    WHERE MID IN
                                    (SELECT MID FROM M_Director 
                                    WHERE PID IN 
                                    (SELECT PID FROM M_Director 
                                    WHERE MID IN 
                                    (SELECT MID FROM Movie 
                                    WHERE (year%4=0) AND (year%100!=0) OR (year%400=0) AND MID IN
                                    (SELECT MID FROM M_Genre 
                                    WHERE GID IN 
                                    (SELECT GID FROM Genre 
                                    WHERE Name LIKE '%Comedy%'))))) 
                                    """, conn)
                                    
Table_for_leap_comedy = pd.read_sql_query("""
                            SELECT p.Name,m.title,m.year,g.Name as Genre
                            FROM Movie m , M_Director md,Genre g,M_Genre mg ,Person p on m.MID = mg.MID
                            AND m.MID = md.MID AND g.Name LIKE '%Comedy%' AND md.PID=p.PID AND m.year%4=0 
                            GROUP BY p.Name,m.title
                            """, conn)

# Question 2
# List the names of all the actors who played in the movie 'Anand' (1971)

Actors_In_Anand = pd.read_sql_query("""
                                    SELECT Name as Actor_Name, Gender 
                                    FROM Movie M 
                                    JOIN M_Cast MC ON M.MID = MC.MID
                                    JOIN Person P ON TRIM(MC.PID) = TRIM(P.PID)
                                    WHERE M.title = 'Anand'
                                    """, conn)

# Question 3
# List all the actors who acted in a film before 1970 and in a film after 1990. (That is: < 1970 and > 1990.)

Actors_timeline = pd.read_sql_query("""
                                    SELECT DISTINCT Name as Actor_Name, Gender 
                                    FROM Person P
                                    WHERE TRIM(PID) IN
                                    (SELECT TRIM(PID) from M_Cast
                                    WHERE MID IN
                                    (SELECT MID from Movie M1
                                    WHERE M1.year > 1990)
                                    AND PID IN
                                    (SELECT PID FROM M_Cast
                                    WHERE MID IN
                                    (SELECT MID FROM Movie M2
                                    WHERE M2.year < 1970)))
                                    """, conn)
                                    
# Question 4
# List all directors who directed 10 movies or more, in descending order of the number of movies they directed. 
# Return the directors' names and the number of movies each of them directed.
Director_Movie_Count = pd.read_sql_query("""
                                         SELECT DISTINCT P.Name Director, Count(*) Number_of_movies
                                         FROM Person P
                                         JOIN M_Director MD ON TRIM(P.PID) = TRIM(MD.PID)
                                         GROUP BY TRIM(MD.PID)
                                         HAVING COUNT(*) >= 10
                                         ORDER BY Number_of_movies DESC
                                         """, conn)
                                
# Question 5
# a) For each year, count the number of movies in that year that had only female actors.
Movie_with_female_actors = pd.read_sql_query("""
                                             SELECT M.year Year, COUNT(*) Number_of_movies 
                                             FROM Movie M
                                             WHERE NOT EXISTS 
                                             (SELECT * from M_Cast MC, Person P
                                             WHERE P.Gender = "Male" AND MC.MID = M.MID
                                             AND MC.PID = P.PID)
                                             GROUP BY Year
                                             """, conn)
                                             
# b)  Now include a small change: report for each year the percentage of movies in that year with only female actors, and the total number of movies made that year. For 
#     example, one answer will be: 1990 31.81 13522 meaning that in 1990 there were 13,522 movies, and 31.81% had only female actors. You do not need to round your answer.

Percent_with_female = pd.read_sql_query("""
                                        SELECT female_count.year Year,((female_count.female_actors_only)*100)/total_count.Total Percentage
                                        FROM ((SELECT movie.year Year,count(*) female_actors_only
                                        FROM movie WHERE NOT EXISTS
                                        (SELECT * FROM M_Cast,person 
                                        WHERE M_Cast.mid = movie.MID AND M_Cast.PID = person.PID AND person.gender='Male' ) \
                                        GROUP BY movie.year) female_count,
                                        (SELECT movie.year,count(*) as Total 
                                        FROM movie group by movie.year) total_count)
                                        WHERE female_count.year=total_count.year
                                        """, conn)

# Question 6
# Find the film(s) with the largest cast. Return the movie title and the size of the cast. 
# By "cast size" we mean the number of distinct actors that played in that movie: if an actor played 
# multiple roles, or if it simply occurs multiple times in casts, we still count her/him only once.

Film_Biggest_CastSize = pd.read_sql_query("""
                                          SELECT M.Title Movie_Name, COUNT(DISTINCT(MC.PID)) Cast_Size
                                          FROM Movie M
                                          JOIN M_Cast MC ON MC.MID = M.MID
                                          GROUP BY M.MID
                                          ORDER BY Cast_Size DESC
                                          """, conn)

# Question 7
#  A decade is a sequence of 10 consecutive years. For example, say in your database you have movie information starting from 1965. 
# Then the first decade is 1965, 1966, ..., 1974; the 
# second one is 1967, 1968, ..., 1976 and so on. Find the decade D with the largest number of films and the total number of films in D.

Decade_with_max_movies = pd.read_sql_query("""
                                           SELECT D.Year Start_Of_Decade, D.Year+9 End_of_Decade, Count(*) Number_of_Movies
                                           FROM
                                           (SELECT DISTINCT Year from Movie) D
                                           JOIN Movie M ON
                                           M.Year >= Start_Of_Decade and M.Year <= End_of_Decade
                                           GROUP BY End_of_Decade
                                           ORDER BY Number_of_Movies DESC
                                           LIMIT 1
                                           """, conn)   
                                        
# Question 8 
# Find the actors that were never unemployed for more than 3 years at a stretch. (Assume that the actors remain unemployed between two consecutive movies)

Unemp_actors_3_years = pd.read_sql_query("""
                                         SELECT Name, Gender FROM Person
                                         WHERE PID NOT IN
                                         (SELECT DISTINCT(PID) FROM M_Cast AS C1
                                         JOIN Movie AS M1
                                         WHERE EXISTS(SELECT MID FROM M_Cast AS C2
                                         JOIN Movie as M2
                                         WHERE C1.PID = C2.PID AND (M2.Year-3)> M1.Year
                                         AND NOT EXISTS 
                                         (SELECT MID FROM M_Cast AS C3
                                         JOIN Movie as M3
                                         WHERE C1.PID = C3.PID
                                         AND M1.Year < M3.Year AND M3.Year < M2.Year)))
                                         """, conn)

# Question 9
#  Find all the actors that made more movies with Yash Chopra than any other director.

Dir_Yash_more = pd.read_sql_query("""
                                  SELECT DISTINCT Name_of_Actor, Count(*) Movies_With_YC 
                                  FROM (SELECT DISTINCT P1.Name as Director, M1.Title as Movie
                                  FROM Person P1
                                  INNER JOIN M_Director MD ON MD.PID = P1.PID
                                  INNER JOIN Movie M1 ON TRIM(MD.MID) = M1.MID
                                  AND P1.Name LIKE '%Yash%' 
                                  GROUP BY P1.Name, M1.Title) T1
                                  INNER JOIN (SELECT DISTINCT P2.Name AS Name_of_Actor, M2.Title AS Movie 
                                  FROM Person P2
                                  INNER JOIN M_Cast MC ON TRIM(MC.PID) = P2.PID
                                  INNER JOIN Movie M2 ON TRIM(MC.MID) = M2.MID
                                  GROUP BY P2.Name, M2.Title) T2
                                  ON T1.Movie = T2.Movie
                                  GROUP BY T2.Name_of_Actor
                                  ORDER BY Movies_With_YC DESC
                                  """, conn)    

# Question 10
# The Shahrukh number of an actor is the length of the shortest path between the actor and Shahrukh Khan in the "co-acting" graph. 
# That is, Shahrukh Khan has Shahrukh number 0; all actors who acted in the same film as Shahrukh have Shahrukh number 1; 
# all actors who acted in the same film as some actor with Shahrukh number 1 have Shahrukh number 2, etc. Return all actors whose Shahrukh number is 2.

Shahrukh_Number_2 = pd.read_sql_query("""
                                      SELECT DISTINCT TRIM(Name) Name
                                      FROM Person P 
                                      INNER JOIN M_Cast MC ON TRIM(MC.PID) = P.PID
                                      INNER JOIN Movie M ON MC.MID = M.MID
                                      AND TRIM(P.Name)!='Shah Rukh Khan'
                                      AND M.Title IN (SELECT DISTINCT Title
                                      FROM Person P3
                                      INNER JOIN M_Cast MC3 ON P3.PID = TRIM(MC3.PID)
                                      AND TRIM(P3.Name) = P3.Name
                                      INNER JOIN Movie M3 ON M3.MID = MC3.MID 
                                      AND P3.Name IN (SELECT DISTINCT Name 
                                      FROM Person P2 
                                      INNER JOIN M_Cast MC2 ON P2.PID = TRIM(MC2.PID)
                                      INNER JOIN Movie M2 ON M2.MID = MC2.MID 
                                      AND TRIM(P2.Name)!='Shah Rukh Khan' AND M2.title IN
                                      (SELECT DISTINCT Title 
                                      FROM Person P3 
                                      INNER JOIN M_Cast MC3 ON P3.PID = TRIM(MC3.PID) 
                                      AND TRIM(P3.Name) = 'Shah Rukh Khan'
                                      INNER JOIN Movie M3 ON M3.MID = MC3.MID)))
                                      ORDER BY Name                                      
                                      """, conn)
