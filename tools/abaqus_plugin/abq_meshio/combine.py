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

            instance = sv1.values[0].instance
            position = sv1.locations[0].position
            if not (
                instance.name == sv2.values[0].instance.name
                and instance.name == sv3.values[0].instance.name
                and instance.name == sv4.values[0].instance.name
                and instance.name == sv5.values[0].instance.name
                and instance.name == sv6.values[0].instance.name
            ):
                print("Could not create field, data is from different instances.")
                break
            if not (
                position == sv2.locations[0].position
                and position == sv3.locations[0].position
                and position == sv4.locations[0].position
                and position == sv5.locations[0].position
                and position == sv6.locations[0].position
            ):
                print(
                    "Could not create field, data from nodes and integration points cannot be combined."
                )
                break

            labels = []
            data = []
            for s1c, s2c, s3c, s4c, s5c, s6c in zip(
                sv1.values, sv2.values, sv3.values, sv4.values, sv5.values, sv6.values,
            ):
                if s1c.precision == SINGLE_PRECISION:
                    data.append(
                        (s1c.data, s2c.data, s3c.data, s4c.data, s5c.data, s6c.data)
                    )
                else:
                    data.append(
                        (
                            s1c.dataDouble,
                            s2c.dataDouble,
                            s3c.dataDouble,
                            s4c.dataDouble,
                            s5c.dataDouble,
                            s6c.dataDouble,
                        )
                    )
                labels.append(s1c.elementLabel)

            # create empty field output
            Field = frame.FieldOutput(
                name=field_name,
                description=desc,
                type=TENSOR_3D_FULL,
                validInvariants=invariants,
            )
            Field.addData(
                position=position, instance=instance, labels=labels, data=data,
            )

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
            instance = sv1.values[0].instance
            position = sv1.locations[0].position
            if not (
                instance.name == sv2.values[0].instance.name
                and instance.name == sv3.values[0].instance.name
            ):
                print("Could not create field, data is from different instances.")
                break
            if not (
                position == sv2.locations[0].position
                and position == sv3.locations[0].position
            ):
                print(
                    "Could not create field, data from nodes and integration points "
                    "cannot be combined."
                )
                break

            labels = []
            data = []
            for s1c, s2c, s3c in zip(sv1.values, sv2.values, sv3.values):
                if s1c.precision == SINGLE_PRECISION:
                    data.append((s1c.data, s2c.data, s3c.data))
                else:
                    data.append((s1c.dataDouble, s2c.dataDouble, s3c.dataDouble))
                if position == INTEGRATION_POINT:
                    labels.append(s1c.elementLabel)
                else:
                    labels.append(s1c.nodeLabel)

            # create empty field output
            Field = frame.FieldOutput(
                name=field_name,
                description=desc,
                type=VECTOR,
                validInvariants=(MAGNITUDE,),
            )
            # fill field output with values
            Field.addData(
                position=position, instance=instance, labels=labels, data=data
            )

    odb.save()
    odb.close()
    odb = session.openOdb(name=odb_name)
    current_viewport = session.currentViewportName
    session.viewports[current_viewport].setValues(displayedObject=odb)
    print("Done.")
    return 1
