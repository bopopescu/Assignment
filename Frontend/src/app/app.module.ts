import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';

import { ReactiveFormsModule } from '@angular/forms';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { CreateStudentsComponent } from './students/create-students/create-students.component';

import { ViewStudentsComponent } from './students/view-students/view-students.component';
import { UpdateStudentsComponent } from './students/update-students/update-students.component';
import { DeleteStudentsComponent } from './students/delete-students/delete-students.component';

@NgModule({
  declarations: [
    AppComponent,
    CreateStudentsComponent,
    ViewStudentsComponent,
    UpdateStudentsComponent,
    DeleteStudentsComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    ReactiveFormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
