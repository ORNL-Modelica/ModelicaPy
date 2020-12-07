within OptimizationDemonstration;
model Demo_1

  package Medium = Modelica.Media.Water.StandardWater;

  parameter Integer nV=10;
  parameter SI.Length length=1.0;
  parameter SI.Length dimension=0.01;
  parameter SI.Temperature T_start=20 + 273.15;
  parameter SI.Pressure p_start=1e5;

  parameter SI.MassFlowRate m_flow = 1;

  // Optimize
  replaceable model HeatTransfer =
      TRANSFORM.Fluid.ClosureRelations.HeatTransfer.Models.DistributedPipe_1D_MultiTransferSurface.Nus_SinglePhase_2Region;
  // End Optimize

  parameter Real CFs[nV] = fill(1.0,nV);

  TRANSFORM.Fluid.Pipes.GenericPipe_MultiTransferSurface
                                         pipe(
    redeclare package Medium = Medium,
    p_a_start=p_start,
    T_a_start=T_start,
    m_flow_a_start=m_flow,
    redeclare replaceable model Geometry =
        TRANSFORM.Fluid.ClosureRelations.Geometry.Models.DistributedVolume_1D.StraightPipe
        (
        dimension=dimension,
        length=length,
        nV=nV),
    use_HeatTransfer=true,
    redeclare model HeatTransfer = HeatTransfer (CFs={{CFs[i] for j in 1:1}
            for i in 1:nV}))
    annotation (Placement(transformation(extent={{-10,-10},{10,10}})));
  TRANSFORM.Fluid.BoundaryConditions.MassFlowSource_T
                                      boundary(
    redeclare package Medium = Medium,
    use_C_in=false,
    m_flow=m_flow,
    T=T_start,
    nPorts=1)
    annotation (Placement(transformation(extent={{-80,-10},{-60,10}})));
  TRANSFORM.Fluid.BoundaryConditions.Boundary_pT
                                 boundary1(
    redeclare package Medium = Medium,
    p=p_start,
    T=T_start,
    nPorts=1) annotation (Placement(transformation(extent={{80,-10},{60,10}})));
  TRANSFORM.HeatAndMassTransfer.BoundaryConditions.Heat.Temperature_multi
    boundary2(nPorts=nV, T=fill(350, nV)) annotation (Placement(transformation(
        extent={{10,-10},{-10,10}},
        rotation=90,
        origin={0,24})));

equation
  connect(boundary.ports[1],pipe. port_a)
    annotation (Line(points={{-60,0},{-10,0}}, color={0,127,255}));
  connect(pipe.port_b, boundary1.ports[1])
    annotation (Line(points={{10,0},{60,0}}, color={0,127,255}));
  connect(boundary2.port, pipe.heatPorts[:, 1])
    annotation (Line(points={{0,14},{0,5}}, color={191,0,0}));
  annotation (Icon(coordinateSystem(preserveAspectRatio=false)), Diagram(
        coordinateSystem(preserveAspectRatio=false)));
end Demo_1;
