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
     * Simply update database file by fetching new
     * data from yahoo.finance and running some insert queries
     *
     * On error returns -1
     * */
int MainDB::fetch_index_json_data(QString quote, QDate start_date, QDate end_date)
{

    //TODO: refactor this into separate class dataManager?
    QNetworkAccessManager nManager;
    QUrl url("http://query.yahooapis.com/v1/public");
    QString method = "yql";
    url.setPath( QString("%1%2").arg(url.path()).arg(method) );

    QString str_start_date=start_date.toString(fetch_date_format);
    QString str_end_date=end_date.toString(fetch_date_format);

    QMap<QString, QVariant>params;
    params["q"]=QString("SELECT * FROM yahoo.finance.historicaldata WHERE symbol =%1 AND startDate=%2 AND endDate=%3").arg(quote).arg(str_start_date).arg(str_end_date);
    params["evn"]=QString("store://datatables.org/alltableswithkeys");
    params["format"]=QString("json");

    //Used to place params in the url
    QUrlQuery urlQuery;
    foreach(QString param, params.keys())
        urlQuery.addQueryItem(param, params[param].toString());

    //reconstruct url from url and set params from urlquery
    url.setQuery(urlQuery);


    QNetworkRequest request(url);

    //TODO: remove curentreply, only leave get(request)?
    QNetworkReply *currentReply = nManager.get(request); //GET
    connect(&nManager, SIGNAL(finished(QNetworkReply *)),this , SLOT(on_QNetworkReplyResult));


    return 0;
}


int MainDB::updateDataBase()
    {

        //TODO: how to update?

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
