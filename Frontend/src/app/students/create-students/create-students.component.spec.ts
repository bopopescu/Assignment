import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateStudentsComponent } from './create-students.component';

describe('CreateStudentsComponent', () => {
  let component: CreateStudentsComponent;
  let fixture: ComponentFixture<CreateStudentsComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ CreateStudentsComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(CreateStudentsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
