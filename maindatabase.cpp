#include "maindatabase.h"

QSqlQueryModel* MainDB::getMainViewModel()
{
    return &queryMainViewModel;
}


int MainDB::setDatabaseName(QString newName="")
{
    if(newName.size()>0)
        db.setDatabaseName(newName);
    return 0;
}

QStringListModel* MainDB::getTablesListModel()
{
    return new QStringListModel(tablesList.keys());
}

/*
* updates mainViewModel with values from tableName
* and performing a join with index table to get name for index_id
*
* On error returns -1
* */
int MainDB::updateMainViewModel(QString tableName)
{
    if(tablesList.keys().contains(tableName) && db_open)
    {
        //Actual name of the table in db
        QString db_tableName = tablesList[tableName];

        //value is the sql thing, so can't bind table name
        //http://stackoverflow.com/questions/15902859/qsqlquery-with-prepare-and-bindvalue-for-column-name-sqlite
        QString sqlStatement =
        QString("SELECT si.index_id as ID, si.name AS Name, t.date, t.value  FROM %1 t INNER JOIN sp_index si ON "
            "si.index_id = t.index_id").arg(db_tableName);


        QSqlQuery q(sqlStatement, db);
        q.exec();

        queryMainViewModel.setQuery(q);

    return 0;
    }
    else
    {
        return -1;
    }

}

    /*
     *
     * update database file by fetching new
     * data from yahoo.finance and running some insert queries
     *
     * On error returns -1
     * */
QScriptValue MainDB::fetch_index_json_data(QString quote, QDate start_date, QDate end_date)
{

    //TODO: refactor this into separate class dataManager?
    QNetworkAccessManager nManager;
    QUrl url("http://query.yahooapis.com/v1/public");
    QString method = "yql";
    url.setPath( QString("%1/%2").arg(url.path()).arg(method) );

    QString str_start_date=start_date.toString(fetch_date_format);
    QString str_end_date=end_date.toString(fetch_date_format);



    //constructing yql query
    QMap<QString, QVariant>params;
    params["evn"]=QString("store://datatables.org/alltableswithkeys");
    params["format"]=QString("json");
    params["q"]=QUrl::toPercentEncoding(
    QString("SELECT*FROM yahoo.finance.historicaldata WHERE symbol='%1' AND startDate='%2' AND endDate='%3'").arg(quote).arg(str_start_date).arg(str_end_date)
    );

    //Used to place params in the url
    QUrlQuery urlQuery;
    foreach(QString param, params.keys())
        urlQuery.addQueryItem(param, params[param].toString());

    //reconstruct url from url and set params from urlquery
    url.setQuery(urlQuery);
    qDebug() <<start_date.toString()<< url.toString();


    QNetworkRequest request(url);

    //TODO: remove curentreply, only leave get(request)?
    QNetworkReply *currentReply; //GET
    currentReply =nManager.get(request);
//    connect(&nManager, SIGNAL(finished(QNetworkReply *)),this , SLOT(on_QNetworkReplyResult));

    QString data = (QString) currentReply->readAll();
    QScriptEngine engine;
    QScriptValue result = engine.evaluate(data);

    return result;
}

int MainDB::updateDatabase()
{
    //	find the latest entry date and set it as start_date
    //	set end_date to today
    //	for every company in sp500
        //	fetch_data as json obj
        //	take out the needed data from json obj
        //	run sql queries to insert new data into db

    //TODO: check if tables exists, if not,  create them

    QVector<QString> sp_companies = this->get_list_sp_companies();

    //find the earliest of latest dates throught all `data` tables
    QString start_date = get_latest_date();
//    QString end_date = QDate::currentDate().toString(fetch_date_format);
    QDate end_date;
    end_date = QDate::fromString(start_date);

//    foreach(QString company, sp_companies)
//    {

//        while(end_date<= QDate::currentDate())
//        {
            QScriptValue res = fetch_index_json_data(sp_companies[1], end_date, end_date.addYears(1));
//            QScriptValueIterator it(res);
//            while(it.hasNext())
//            {
//                it.next();
//            }
            qDebug()<<res.toString();

//        }
//    }




//    insert_new_data_row("hui", t,v);
//    QScriptValue res = fetch_index_json_data()

    //insert newly received data into the database


return 0;

}

void MainDB::on_QNetworkReplyResult(QNetworkReply *reply)
{
    if(reply->error() != QNetworkReply::NoError)
    {
        qDebug()<<"QNetworkReply error";
        //TODO: handle error
        return;
    }

    QString data=(QString)reply->readAll();

    QScriptEngine engine;
    QScriptValue result = engine.evaluate(data);


}

    int MainDB::insert_new_data_row(QString tableName, QVector<QString> columnsNames, QVector<QString> values)
{
    QString str=QString("INSERT INTO %1 (").arg(tableName);

    //basically i want to generate sql statement for any table with any
    //number of columns.


    //TODO: rewrite with foreach loop and make use of prepared statements
    for (int i =0; i < columnsNames.length(); i++)
    {
        //if the last element to be added
        //don't add trailing ',' but add ')'
        if (i==columnsNames.length()-1)
        {
            str+=columnsNames[i];
            str+=") values(";
        }
        else
        {
            str+=columnsNames[i];
            str+=",";
        }
    }

    for (int i =0 ; i < values.length(); i++)
    {
        if (i==values.length()-1)
        {
         str+="'"+values[i]+"')";
        }
        else
        {
         str+="'"+values[i]+"',";

        }
    }

    QSqlQuery q(str, db);
    q.exec();


    //TODO: check errors and return approp return values
    return 0;
}


 QString MainDB::get_latest_date()
{
    //TODO: rewrite so that latest date is kept somewhere in a table and is
    //			updated along with data



    //QSQL can't run milti-lined sql statemnt;
     QString sqlStatement ="";
     QVector<QString> statement_list;
        statement_list.push_back("drop table if exists tables_maxes;");
        statement_list.push_back("create table tables_maxes(max integer);");

        statement_list.push_back("insert into tables_maxes(max) select max(date) from sp_adj_close;");
        statement_list.push_back("insert into tables_maxes(max) select max(date) from sp_high;");
        statement_list.push_back("insert into tables_maxes(max) select max(date) from sp_index_adj_close;");
        statement_list.push_back("insert into tables_maxes(max) select max(date) from sp_index_close;");
        statement_list.push_back("insert into tables_maxes(max) select max(date) from sp_index_high;");
        statement_list.push_back("insert into tables_maxes(max) select max(date) from sp_index_low;");
        statement_list.push_back("insert into tables_maxes(max) select max(date) from sp_index_open;");
        statement_list.push_back("insert into tables_maxes(max) select max(date) from sp_index_volume;");
        statement_list.push_back("insert into tables_maxes(max) select max(date) from sp_low;");
        statement_list.push_back("insert into tables_maxes(max) select max(date) from sp_open;");
        statement_list.push_back("insert into tables_maxes(max) select max(date) from sp_volume;");


        foreach(QString sqlquery, statement_list)
        {
            QSqlQuery q(sqlquery, db);
            q.exec();

        }


        QSqlQuery q("select max(max) from tables_maxes;", db);
        q.next();
        return q.value(0).toString();

}


 QVector<QString> MainDB::get_list_sp_companies()
{

    QVector<QString> sp_companies;
    QString sqlStatement = QString(
    "SELECT name FROM sp_index;"
    );

    QSqlQuery q(sqlStatement,db);

    while(q.next())
    {
        sp_companies.push_back(q.value(0).toString());
    }
        return sp_companies;

}
