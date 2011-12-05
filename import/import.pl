#!/usr/bin/perl
use strict;
use DBI;
use Term::ProgressBar;

print "Connecting to the database\n";
my $dbh = DBI->connect("dbi:SQLite:dbname=db.sqlite", "", "", {AutoCommit => 0}) or die $!;
#my $dbh = DBI->connect("dbi:Pg:dbname=imdb", "", "", {AutoCommit => 0}) or die $!;

sub year {
    if (m/\(([0-9]{4})[^\)]*\)/) {
        return $1;
    }
    else {
        return 0;
    }
}

sub valid_year {
    my $min_year = 2010; # 2000 in the assignment
    my $max_year = 2010;
    return ($_[0] >= $min_year and $_[0] <= $max_year);
}        

sub import_movies {
    my ($id, $serie_id, $date, $year, $end_year, $title, $epi_title, $season, $epi_number);
    my $work_sth = $dbh->prepare("insert into Work (ID, Title, Year) values (?, ?, ?)");
    my $movie_sth = $dbh->prepare("insert into Movie (ID) values (?)");
    my $serie_sth = $dbh->prepare("insert into Serie (ID, EndYear) values (?, ?)");
    my $epi_sth = $dbh->prepare("insert into Episode (ID, Season, EpisodeNum, Date, EpisodeTitle) values (?, ?, ?, ?, ?)");
    my $epi_serie_sth = $dbh->prepare("insert into SerieEpisode (SID, EID) values (?, ?)");
    my $progress = Term::ProgressBar->new({name => "Importing movies",
                                           count => int(`wc -l movies.list`)});
    my $start = time();
    
    open(FILE, '<', "movies.list") or die $!;

    while (<FILE>) {
        $progress->update();
        if (m/([^	]+)	+([0-9\?]{4})-?([0-9\?]{4})?/) {
            $id = $1;
            $year = $2;
            $end_year = $3;
            # TODO: maybe don't filter here but with $date later, to
            # avoid some foreign key problems with other files ?
            if (valid_year($year)) {
                if ($id =~ /"(.+)" \(([0-9]{4})[^\)]*\) \{(.*)\(#([0-9]{1,3})\.([0-9]{1,3})\)\}$/) {
                    $title = $1;
                    $date = $2;
                    $epi_title = $3;
                    $season = $4;
                    $epi_number = $5;
                    if (valid_year($year)) {
                        # don't add an episode from a serie started before 2000
                        ($serie_id) = split(/ {/, $id);
                        $work_sth->execute($id, $title, $date) or die $work_sth->errstr;
                        $epi_sth->execute($id, $season, $epi_number, $year, $epi_title) or die $epi_sth->errstr;
                        $epi_serie_sth->execute($serie_id, $id) or die $epi_sth->errstr;
                    }
                }
                elsif ($id =~ /\"(.+)\" \(([0-9]{4})[^\)]*\)$/) {
                    $title = $1;
                    $date = $2;
                    if ($end_year eq "????" or $end_year eq "") {
                        $end_year = undef;
                    }
                    $work_sth->execute($id, $title, $year) or die $work_sth->errstr;
                    $serie_sth->execute($id, $end_year) or die $serie_sth->errstr;
                    $dbh->commit();
                }
                elsif ($id =~ /(.+) \(([0-9]{4})[^\)]*\)$/) {
                    $title = $1;
                    $date = $2;
                    $work_sth->execute($id, $title, $year) or die $work_sth->errstr;
                    $movie_sth->execute($id) or die $movie_sth->errstr;
                }
            }
        }
    }
    $dbh->commit();
    close(FILE);
    print "It took ", time() - $start, " seconds\n";
}

sub import_countries {
    my ($id, $year, $country);
    my $sth = $dbh->prepare("insert into Country (ID, Country) values (?, ?)");
    my $progress = Term::ProgressBar->new({name => "Importing countries",
                                           count => int(`wc -l countries.list`)});
    my $start = time();

    open(FILE, '<', "countries.list") or die $!;

    while (<FILE>) {
        $progress->update();
        if (m/([^	]+)	+([a-zA-Z]+)/) {
            $id = $1;
            $country = $2;
            if (valid_year(year($id))) {
                # ignore the error since there are doubles in countries.list
                $sth->execute($id, $country);
            }
        }
    }
    $dbh->commit();
    close(FILE);
    print "It took ", time() - $start, " seconds\n";
}

sub import_languages {
    my ($id, $year, $lang);
    my $sth = $dbh->prepare("insert into Language (ID, Language) values (?, ?)");
    my $progress = Term::ProgressBar->new({name => "Importing languages",
                                           count => int(`wc -l language.list`)});
    my $start = time();

    open(FILE, '<', "language.list") or die $!;
    while (<FILE>) {
        $progress->update();
        if (m/([^	]+)	+([a-zA-Z]+)/) {
            $id = $1;
            $lang = $2;
            if (valid_year(year($id))) {
                $sth->execute($id, $lang);
            }
        }
    }
    $dbh->commit();
    close(FILE);
    print "It took ", time() - $start, " seconds\n";
}

sub import_genres {
    my ($id, $year, $genre);
    my $sth = $dbh->prepare("insert into Genre (ID, Genre) values (?, ?)");
    my $progress = Term::ProgressBar->new({name => "Importing genres",
                                           count => int(`wc -l genres.list`)});
    my $start = time();

    open(FILE, '<', "genres.list") or die $!;
    while (<FILE>) {
        $progress->update();
        if (m/([^	]+)	+([a-zA-Z]+)/) {
            $id = $1;
            $genre = $2;
            if (valid_year(year($id))) {
                $sth->execute($id, $genre);
            }
        }
    }
    $dbh->commit();
    close(FILE);
    print "It took ", time() - $start, " seconds\n";
}

sub import_directors {
    my ($firstname, $lastname, $number, $id, $year);
    # The format doesn't says anything about the gender
    my $person_sth = $dbh->prepare("insert into Person (FirstName, LastName, Num) values (?, ?, ?)");
    my $director_sth = $dbh->prepare("insert into Director (FirstName, LastName, Num, ID) values (?, ?, ?, ?)");
    my $progress = Term::ProgressBar->new({name => "Importing directors",
                                           count => int(`wc -l directors.list`)});
    my $start = time();

    open(FILE, '<', "directors.list") or die $!;
    while (<FILE>) {
        $progress->update();
        if (m/([^	]+)	+(.+)/) {
            # new director
            $_ = $1;
            $id = $2;
            if (m/([^,]+)(, ([^\(	]+))?( \(([IVXLM]+)\))?$/) {
                $lastname = $1;
                $firstname = $3;
                $number = $5;
                if (not defined $number) {
                    $number = '';
                }
                $person_sth->execute($firstname, $lastname, $number);
                $dbh->commit();
                if (valid_year(year($id))) {
                    $director_sth->execute($firstname, $lastname, $number, $id);
                }
            }
            else {
                print $_, "\n";
                print "Incorrect person definition, this might introduce bad values to the database\n";
            }
        }
        elsif (m/^	+(.+)/) {
            $id = $1;
            if (valid_year(year($id))) {
                $director_sth->execute($firstname, $lastname, $number, $id);
            }
        }
    }
    $dbh->commit();
    close(FILE);
    print "It took ", time() - $start, " seconds\n";
}

sub import_writers {
    my ($firstname, $lastname, $number, $id, $year);
    # The format doesn't says anything about the gender
    my $person_sth = $dbh->prepare("insert into Person (FirstName, LastName, Num) values (?, ?, ?)");
    my $writer_sth = $dbh->prepare("insert into Writer (FirstName, LastName, Num, ID) values (?, ?, ?, ?)");
    my $progress = Term::ProgressBar->new({name => "Importing writers",
                                           count => int(`wc -l writers.list`)});
    my $start = time();

    open(FILE, '<', "writers.list") or die $!;
    while (<FILE>) {
        $progress->update();
        if (m/([^	]+)	+(.+)/) {
            # new writer
            # if the person is already present, we rely on the DBMS
            # *not* to add this to the database (sqlite and postgresql
            # do this)
            $_ = $1;
            $id = $2;
            if (m/([^,]+)(, ([^\(	]+))?( \(([IVXLM]+)\))?$/) {
                $lastname = $1;
                $firstname = $3;
                $number = $5;
                if (not defined $number) {
                    $number = '';
                }
                $person_sth->execute($firstname, $lastname, $number);
                $dbh->commit();
                if (valid_year(year($id))) {
                    $writer_sth->execute($firstname, $lastname, $number, $id);
                }
            }
            else {
                print $_, "\n";
                print "Incorrect person definition, this might introduce bad values to the database\n";
            }

        }
        elsif (m/^	+(.+)/) {
            $id = $1;
            if (valid_year(year($id))) {
                $writer_sth->execute($firstname, $lastname, $number, $id);
            }
        }
    }
    $dbh->commit();
    close(FILE);
    print "It took ", time() - $start, " seconds\n";
}

sub import_actors {
    my $gender = $_[0];
    my ($firstname, $lastname, $number, $id, $year, $role, $file);
    my $person_sth = $dbh->prepare("insert into Person (FirstName, LastName, Num, Gender) values (?, ?, ?, ?)");
    my $actor_sth = $dbh->prepare("insert into Actor (FirstName, LastName, Num, ID, Role) values (?, ?, ?, ?, ?)");
    if ($gender eq "M") {
        $file = "actors.list";
    }
    elsif ($gender eq "F") {
        $file = "actresses.list";
    }
    else {
        die ("Unknown gender: " . $gender);
    }
    my $progress = Term::ProgressBar->new({name => "Importing actors ($gender)",
                                           count => int(`wc -l $file`)});
    my $start = time();

    open(FILE, '<', $file);

    while (<FILE>) {
        $progress->update();
        if (m/([^	]+)	+([^\[]+)  \[([^\]]+)\]/) {
            # new actor
            $_ = $1;
            $id = $2;
            $role = $3;
            if (m/([^,]+)(, ([^\(	]+))?( \(([IVXLM]+)\))?$/) {
                $lastname = $1;
                $firstname = $3;
                if (not defined $firstname) {
                    $firstname = '';
                }
                $number = $5;
                if (not defined $number) {
                    $number = '';
                }
                $person_sth->execute($firstname, $lastname, $number, $gender);
                $dbh->commit();
                if (valid_year(year($id))) {
                    $actor_sth->execute($firstname, $lastname, $number, $id, $role);
                }
            }
            else {
                print $_, "\n";
                print "Incorrect person definition, this might introduce bad values to the database\n";
            }

        }
        elsif (m/^	+([^\[]+)  \[([^\]]+)\]/) {
            $id = $1;
            $role = $2;
            if (valid_year(year($id))) {
                $actor_sth->execute($firstname, $lastname, $number, $id, $role);
            }
        }
    }
    $dbh->commit();
    close(FILE);
    print "It took ", time() - $start, " seconds\n";
}

sub import_actors_male {
    import_actors("M");
}

sub import_actors_female {
    import_actors("F");
}

sub clean_db {
    print "Cleaning the database\n";
    # remove persons who don't have played/directed/wrote something
    # from the 2000's (in case foreign constraints aren't active, like
    # in sqlite)
    $dbh->do("delete from Person where not exists (select A.FirstName from Actor A where A.FirstName = Person.FirstName and A.LastName = Person.LastName and A.Num = Person.Num union select W.FirstName from Writer W where W.FirstName = Person.FirstName and W.LastName = Person.LastName and W.Num = Person.Num union select D.FirstName from Director D where D.FirstName = Person.FirstName and D.LastName = Person.LastName and D.Num = Person.Num)");
}

sub import_everything {
    import_movies;
    import_countries;
    import_languages;
    import_genres;
    import_actors_male;
    import_actors_female;
    import_directors;
    import_writers;
}

sub create_tables {
    `sqlite3 db.sqlite '.read create.sql'`;
}

sub quit {
    print "Disconnecting from the database\n";
    $dbh->disconnect();
    exit 0;
}

my @choices = ( "Create the tables",
                "Import everything", "Import movies.list",
                "Import countries.list", "Import languages.list",
                "Import genres.list", "Import directors.list",
                "Import writers.list", "Import actors.list",
                "Import actresses.list", "Clean the database",
                "Quit",
    );
my @functions = ( \&create_tables,
                  \&import_everything, \&import_movies,
                  \&import_countries, \&import_languages,
                  \&import_genres, \&import_directors,
                  \&import_writers, \&import_actors_male,
                  \&import_actors_female, \&clean_db,
                  \&quit,
    );
my $max_choice = @choices;
my $input;

do {
    print "What to do?\n";
    for (my $i = 0; $i < $max_choice; $i++) {
        print $i, ". ", $choices[$i], "\n";
    }
    $input = <>;
    if ($input eq "") {
        quit();
    }
    else {
        $input = int($input);
    }
    if ($input >= 0 and $input <= $max_choice) {
        $functions[$input]();
    }
} while (1);
