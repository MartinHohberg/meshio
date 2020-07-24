"""Combine several state variables to new variables in Abaqus."""
from abaqus import milestone, session
from abaqusConstants import (
    INTEGRATION_POINT,
    MAGNITUDE,
    MAX_PRINCIPAL,
    MID_PRINCIPAL,
    MIN_PRINCIPAL,
    SINGLE_PRECISION,
    TENSOR_3D_FULL,
    VECTOR,
)


def tensor(odb_name, field_name, desc, s1, s2, s3, s4, s5, s6):
    """Build a tensor.

    Parameters
    ----------
    odb_name : str
        Name of output databse.
    field_name : str
        Name of field to be generated.
    desc : str
        Description of field to be generated.
    s1 : str
        Name of 11 component.
    s2 : str
        Name of 22 component.
    s3 : str
        Name of 33 component.
    s4 : str
        Name of 12 component.
    s5 : str
        Name of 23 component.
    s6 : str
        Name of 13 component.

    """
    # close ODB and open with write permissions
    odb = session.openOdb(name=odb_name)
    odb.close()
    odb = session.openOdb(name=odb_name, readOnly=False)
    # define invariants to be computed
    invariants = (MAX_PRINCIPAL, MID_PRINCIPAL, MIN_PRINCIPAL)

    # for each step
    for stepName in odb.steps.keys():
        # for each frame
        N = len(odb.steps[stepName].frames)
        for i, frame in enumerate(odb.steps[stepName].frames):
            milestone("Adding field to frames in step %s" % stepName, "Frame", i, N)
            sv1 = frame.fieldOutputs[s1]
            sv2 = frame.fieldOutputs[s2]
            sv3 = frame.fieldOutputs[s3]
            sv4 = frame.fieldOutputs[s4]
            sv5 = frame.fieldOutputs[s6]  # different order in ODB (WTF ABQ?!)
            sv6 = frame.fieldOutputs[s5]  # different order in ODB (WTF ABQ?!)

            # create empty field output
            Field = frame.FieldOutput(
                name=field_name,
                description=desc,
                type=TENSOR_3D_FULL,
                validInvariants=invariants,
            )

            _add_to_field(Field, odb, sv1, sv2, sv3, sv4, sv5, sv6)

    odb.save()
    odb.close()
    odb = session.openOdb(name=odb_name)
    current_viewport = session.currentViewportName
    session.viewports[current_viewport].setValues(displayedObject=odb)
    print("Done.")
    return 1


def vector(odb_name, field_name, desc, s1, s2, s3):
    """Build a vector.

    Parameters
    ----------
    odb_name : str
        Name of output databse.
    field_name : str
        Name of field to be generated.
    desc : str
        Description of field to be generated.
    s1 : str
        Name of 11 component.
    s2 : str
        Name of 22 component.
    s3 : str
        Name of 33 component.

    """
    # close ODB and open with write permissions
    odb = session.openOdb(name=odb_name)
    odb.close()
    odb = session.openOdb(name=odb_name, readOnly=False)

    # for each step
    for stepName in odb.steps.keys():
        # for each frame
        N = len(odb.steps[stepName].frames)
        for i, frame in enumerate(odb.steps[stepName].frames):
            milestone("Adding field to frames in step %s" % stepName, "Frame", i, N)
            sv1 = frame.fieldOutputs[s1]
            sv2 = frame.fieldOutputs[s2]
            sv3 = frame.fieldOutputs[s3]

            # create empty field output
            Field = frame.FieldOutput(
                name=field_name,
                description=desc,
                type=VECTOR,
                validInvariants=(MAGNITUDE,),
            )

            _add_to_field(Field, odb, sv1, sv2, sv3)

    odb.save()
    odb.close()
    odb = session.openOdb(name=odb_name)
    current_viewport = session.currentViewportName
    session.viewports[current_viewport].setValues(displayedObject=odb)
    print("Done.")
    return 1


def _add_to_field(Field, odb, *args):
    import numpy as np

    labels = {}
    data = {}
    section_points = {}
    for svals in zip(*[a.values for a in args]):
        instance_name = svals[0].instance.name
        position = svals[0].position
        precision = svals[0].precision
        section_point = svals[0].sectionPoint
        section_number = svals[0].sectionPoint.number

        # Check wether they are from same instance
        if not all([instance_name == s.instance.name for s in svals]):
            print("Could not create field, data is from different instances.")
            break

        if precision == SINGLE_PRECISION:
            data_tuple = tuple([s.data for s in svals])
        else:
            data_tuple = tuple([s.dataDouble for s in svals])

        if position == INTEGRATION_POINT:
            label = svals[0].elementLabel
        else:
            label = svals[0].nodeLabel

        # build dictionary
        if instance_name in data.keys():
            if section_number in data[instance_name].keys():
                data[instance_name][section_number].append(data_tuple)
                labels[instance_name][section_number].append(label)
                section_points[instance_name][section_number] = section_point
            else:
                data[instance_name][section_number] = [data_tuple]
                labels[instance_name][section_number] = [label]
                section_points[instance_name][section_number] = section_point
        else:
            data[instance_name] = {section_number: [data_tuple]}
            labels[instance_name] = {section_number: [label]}
            section_points[instance_name] = {section_number: section_point}

    # fill field output with values
    for instance_name in data.keys():
        instance = odb.rootAssembly.instances[instance_name]
        for section_number in data[instance_name].keys():
            Field.addData(
                position=position,
                instance=instance,
                labels=labels[instance_name][section_number],
                data=data[instance_name][section_number],
                sectionPoint=section_points[instance_name][section_number],
            )
