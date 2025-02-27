#!/usr/bin/env nextflow

#Nextflow pipeline to run all the proteomic analysis scripts in serial order
#Please run this together with the config file to execute in batch mode (please confirm SLURM settings before running)


nextflow.enable.dsl=2

process Database_create {
    input:
    path params.database_script

    output:
    path 'database_output'

    script:
    """
    python ${params.database_script}
    """
}

process Manifest_create {
    input:
    path 'database_output'
    path params.manifest_script

    output:
    path 'manifest_output'

    script:
    """
    python ${params.manifest_script}
    """
}

process Launch_analysis {
    input:
    path 'manifest_output'
    path params.launch_script

    script:
    """
    bash ${params.launch_script}
    """
}

process Annotate {
    input:
    path params.annotate_script

    output:
    path 'annotate_output'

    script:
    """
    python ${params.annotate_script}
    """
}

process Binding_affinity {
    input:
    path 'annotate_output'
    path params.binding_script

    script:
    """
    python ${params.binding_script}
    """
}

workflow {
    database_create = Database_create(params.database_script)
    manifest_create = Manifest_create(database_create.out, params.manifest_script)
    launch_analysis = Launch_analysis(manifest_create.out, params.launch_script)
    annotate = Annotate(params.annotate_script)
    binding_affinity = Binding_affinity(annotate.out, params.binding_script)
}

