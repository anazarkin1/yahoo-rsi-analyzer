#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "maindatabase.h"

const QString PATH ="/home/alex/Dropbox/Projects/Python/spindex_download/sp.db";
MainDB dbManager(0,PATH);
MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);
    ui->lvTablesList->setModel(dbManager.getTablesListModel());
//    ui->tvMainView->setModel(dbManager.getTableData());


    /*
        Signal - Slot connections:
    */
    connect(ui->btnUpdateAll, SIGNAL(clicked()), this, SLOT(on_btnUpdateAll_clicked()));

    /* End of Signal - Slot connections*/

}

MainWindow::~MainWindow()
{
    delete ui;
}



void MainWindow::on_lvTablesList_clicked(const QModelIndex &index)
{
    ui->txtLog->append(index.data().toString());

    //Can update mainView through functions such as
    //updateMainViewModel()
    ui->tvMainView->setModel(dbManager.getMainViewModel());
    dbManager.updateMainViewModel(index.data().toString());


}


void MainWindow::on_btnUpdateAll_clicked()
{
    //TODO: Clicking on button crashes the program, problem is in the slot-signal stuff
    if (dbManager.updateDataBase() !=0 )
    {
        //TODO: Handle error
    }

}
