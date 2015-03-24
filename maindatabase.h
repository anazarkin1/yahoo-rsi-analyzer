#ifndef MAINDATABASE_H
#define MAINDATABASE_H

#endif // MAINDATABASE_H

#include <QtSql>
#include <QStringList>
#include <QStringListModel>
#include <QAbstractItemView>

class MainDB : QObject
{
    private:
    QSqlDatabase db;
    QHash<QString, QString> tablesList;
    QSqlQueryModel queryMainViewModel;
    bool db_open;

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
    QSqlQueryModel* getMainViewModel()
    {
            return &queryMainViewModel;
    }


    int setDatabaseName(QString newName="")
    {
        if(newName.size()>0)
            db.setDatabaseName(newName);
        return 0;
    }

    QStringListModel* getTablesListModel()
    {
        return new QStringListModel(tablesList.keys());
    }

    /*
     * updates mainViewModel with values from tableName
     * and performing a join with index table to get name for index_id
     *
     * On error returns -1
     * */
    int updateMainViewModel(QString tableName)
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


    int updateDataBase()
    {
        //TODO: write actual update db code

        return -1;

    }




};
