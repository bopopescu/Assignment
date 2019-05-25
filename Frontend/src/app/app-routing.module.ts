import { NgModule } from '@angular/core';
import {RouterModule, Routes } from '@angular/router'


// Import the components so they can be referenced in routes
import { CreateStudentsComponent } from './students/create-students/create-students.component';
import { ViewStudentsComponent } from './students/view-students/view-students.component';
import { DeleteStudentsComponent } from './students/delete-students/delete-students.component';
import { UpdateStudentsComponent } from './students/update-students/update-students.component';
// The last route is the empty path route. This specifies
// the route to redirect to if the client side path is empty.
const appRoutes: Routes = [
 { path: 'add', component: CreateStudentsComponent },
 { path: 'view', component: ViewStudentsComponent },
 { path: 'update', component: UpdateStudentsComponent },
 { path: 'delete', component: DeleteStudentsComponent },
];

@NgModule({
  imports: [
    RouterModule.forRoot(appRoutes)
  ],
  exports:[RouterModule]

})
export class AppRoutingModule { }
