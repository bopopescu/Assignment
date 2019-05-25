import { Component, OnInit } from '@angular/core';

import { FormGroup, FormControl } from '@angular/forms';
@Component({
  selector: 'app-create-students',
  templateUrl: './create-students.component.html',
  styleUrls: ['./create-students.component.css']
})
export class CreateStudentsComponent implements OnInit {
  addstudentForm : FormGroup
  constructor() { }

  ngOnInit() {
    this.addstudentForm = new FormGroup({
      Name : new FormControl(),
      Email : new FormControl(),
      address : new FormControl(),
      phone : new FormControl(),
      date_of_birth : new FormControl(),

    })
  }

}
