#ifndef MAINDATABASE_H
#define MAINDATABASE_H

#endif // MAINDATABASE_H

#include <QtSql>
#include <QStringList>
#include <QStringListModel>
#include <QAbstractItemView>
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QScriptEngine>

class MainDB : QObject
{
    private:
    QSqlDatabase db;
    QHash<QString, QString> tablesList;
    QSqlQueryModel queryMainViewModel;

    //format is 2014-12-01
    const QString fetch_date_format = "yyyy-MM-dd";

    bool db_open;

    //TODO: refactor constructor's implementation into header file
    public:
    MainDB(QObject *parent=0, QString dbpath=""):QObject(parent=0)
    {
        db_open=false;
        db = QSqlDatabase::addDatabase("QSQLITE");
        this->setDatabaseName(dbpath);

        /*List of Tables that are available for users*/
        this->tablesList["Low"] = "sp_low";
        tablesList["Open"] = "sp_open";
        tablesList["Close"] = "sp_close";
        tablesList["High"] = "sp_high";
        tablesList["Adj Close"] = "sp_adj_close";
        tablesList["Volume"] = "sp_volume";
        tablesList["Index"] = "sp_index";


        /*Try to open database
         * Later always check value of db_open before running queries
         * on the database
        */
        db_open = db.open();

    }
    QSqlQueryModel* getMainViewModel();


    int setDatabaseName(QString newName);

    QStringListModel* getTablesListModel();

    /*
     * updates mainViewModel with values from tableName
     * and performing a join with index table to get name for index_id
     *
     * On error returns -1
     * */
    int updateMainViewModel(QString tableName);

    /*
     *
     * Simply update database file by fetching new
     * data from yahoo.finance and running some insert queries
     *
     * On error returns -1
     * */
    QScriptValue fetch_index_json_data(QString quote, QDate start_date, QDate end_date);

    /*
     *	Return the latest date entered into the database's data tables
     * */
    QString get_latest_date();


    int updateDatabase();

    void on_QNetworkReplyResult(QNetworkReply *reply);


};

