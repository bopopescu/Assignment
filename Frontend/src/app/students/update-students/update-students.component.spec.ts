import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { UpdateStudentsComponent } from './update-students.component';

describe('UpdateStudentsComponent', () => {
  let component: UpdateStudentsComponent;
  let fixture: ComponentFixture<UpdateStudentsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ UpdateStudentsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(UpdateStudentsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
