% Android Architecture, Part 2
% Andrew Nichols
% 17 April 2017

After bulding the basics of my [android app](android1.html), I had a simple app that could display/edit lists of school terms. The problem? The requirements specified that the app have terms, courses associated with each term, assessments associated with each course, and notes associated with each course *or* assessment.

That was fine, after all I was armed with all kinds of SQL database design knowledge after 3 courses at WGU, so I rapidly stubbed out java classes for each of these entities. Each relationship was a simple many-to-one relationship, so `Course` table needed to maintain a foreign key pointing to the associated `Term`, the `Assessment` table needed to maintain a foreign key pointing to the associated `Course`, and so on.

Each class handled it's own table definition rules, and my `DBHelper` class now opened the database, then when needing to create or upgrade, called methods from each entitiy class to create each table. Add some sample data in my main activity's `onCreate` method, and... `Exceptions: table course does not exist`. Since the database already existed and I hadn't incremented the verison number, rerunning my app and calling more table creation methods did nothing. My very hacky fix was to uninstall the app and then reload it onto the emulator, although I just now realized that a more sensible idea would have been to create a simple method in the `DBHelper` to drop all the tables and delete the database, then tie this to a menu action. Lesson learned.

My database redefined, I turned to listing all the courses. And ran into the `ContentProvider`, which in its `insert`, `update`, and `delete` methods was referring directly to the `Term` class. Did I need separate providers for each table? That didn't seem right.

After chewing on the problem for a while (and sleeping on it, which always helps me), I settled on the pattern explained in [this stackoverflow post](http://stackoverflow.com/questions/3814005/best-practices-for-exposing-multiple-tables-using-content-providers-in-android). I didn't realize it at the time, but this style is used internally by android as well. An example, from my finished ContentProvider:

```
@Override
public int update(
		Uri uri, 
		ContentValues values, 
		String selection, 
		String[] selectionArgs) {

	String table;

	switch (uriMatcher.match(uri)) {
		case TERMS:
			table = Term.TABLE; break;
		case COURSES:
			table = Course.TABLE; break;
		case ASSESSMENTS:
			table = Assessment.TABLE; break;
		case COURSE_NOTES:
			table = CourseNote.TABLE; break;
		case ASSESSMENT_NOTES:
			table = AssessmentNote.TABLE; break;
		default:
			table = ""; break;
	}
	return !table.isEmpty() ?
		database.update(table,
				values,
				selection,
				selectionArgs) : 0;
}
```

This general pattern proved hugely useful, so that the `ContentProvider` handled most aspects of interacting with the database correctly, so long as it was given the proper URI, which are defined as public constants in the `ContentProvider` itself. Because it was also necessary for courses to understand what term they were in and build the appropriate WHERE clause, the classes are sadly fairly coupled together, but having the `ContentProvider` handle most aspects of DB interaction is a step in the right direction. Further refactoring could likely reduce coupling throughout the codebase.

From this point on, I implemented the entire database structure as specified by the requirements, absent pictures in notes, which I decided to save for another day.
