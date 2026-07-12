/* ------------------------------------------------------------
name: "clave"
Code generated with Faust 2.70.3 (https://faust.grame.fr)
Compilation options: -lang cpp -ct 1 -cn Clave -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0
------------------------------------------------------------ */

#ifndef  __Clave_H__
#define  __Clave_H__

#ifndef FAUSTFLOAT
#define FAUSTFLOAT float
#endif 

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <math.h>

#ifndef FAUSTCLASS 
#define FAUSTCLASS Clave
#endif

#ifdef __APPLE__ 
#define exp10f __exp10f
#define exp10 __exp10
#endif

#if defined(_WIN32)
#define RESTRICT __restrict
#else
#define RESTRICT __restrict__
#endif

static float Clave_faustpower2_f(float value) {
	return value * value;
}

class Clave : public dsp {
	
 private:
	
	int fSampleRate;
	float fConst0;
	float fConst3;
	float fConst5;
	float fConst7;
	FAUSTFLOAT fHslider0;
	float fConst8;
	FAUSTFLOAT fButton0;
	float fVec0[2];
	float fRec1[3];
	float fRec0[3];
	int iRec2[2];
	float fConst9;
	float fConst10;
	FAUSTFLOAT fHslider1;
	FAUSTFLOAT fHslider2;
	float fConst11;
	
 public:
	Clave() {}

	void metadata(Meta* m) { 
		m->declare("basics.lib/name", "Faust Basic Element Library");
		m->declare("basics.lib/tabulateNd", "Copyright (C) 2023 Bart Brouns <bart@magnetophon.nl>");
		m->declare("basics.lib/version", "1.12.0");
		m->declare("compile_options", "-lang cpp -ct 1 -cn Clave -es 1 -mcd 16 -mdd 1024 -mdy 33 -single -ftz 0");
		m->declare("envelopes.lib/ar:author", "Yann Orlarey, Stéphane Letz");
		m->declare("envelopes.lib/author", "GRAME");
		m->declare("envelopes.lib/copyright", "GRAME");
		m->declare("envelopes.lib/license", "LGPL with exception");
		m->declare("envelopes.lib/name", "Faust Envelope Library");
		m->declare("envelopes.lib/version", "1.3.0");
		m->declare("filename", "clave.dsp");
		m->declare("filters.lib/fir:author", "Julius O. Smith III");
		m->declare("filters.lib/fir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/fir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/highpass:author", "Julius O. Smith III");
		m->declare("filters.lib/highpass:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:author", "Julius O. Smith III");
		m->declare("filters.lib/iir:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/iir:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1", "MIT-style STK-4.3 license");
		m->declare("filters.lib/lowpass0_highpass1:author", "Julius O. Smith III");
		m->declare("filters.lib/name", "Faust Filters Library");
		m->declare("filters.lib/resonbp:author", "Julius O. Smith III");
		m->declare("filters.lib/resonbp:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/resonbp:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/tf2s:author", "Julius O. Smith III");
		m->declare("filters.lib/tf2s:copyright", "Copyright (C) 2003-2019 by Julius O. Smith III <jos@ccrma.stanford.edu>");
		m->declare("filters.lib/tf2s:license", "MIT-style STK-4.3 license");
		m->declare("filters.lib/version", "1.3.0");
		m->declare("maths.lib/author", "GRAME");
		m->declare("maths.lib/copyright", "GRAME");
		m->declare("maths.lib/license", "LGPL with exception");
		m->declare("maths.lib/name", "Faust Math Library");
		m->declare("maths.lib/version", "2.7.0");
		m->declare("name", "clave");
		m->declare("platform.lib/name", "Generic Platform Library");
		m->declare("platform.lib/version", "1.3.0");
	}

	virtual int getNumInputs() {
		return 0;
	}
	virtual int getNumOutputs() {
		return 2;
	}
	
	static void classInit(int sample_rate) {
	}
	
	virtual void instanceConstants(int sample_rate) {
		fSampleRate = sample_rate;
		fConst0 = std::min<float>(1.92e+05f, std::max<float>(1.0f, float(fSampleRate)));
		float fConst1 = std::tan(1884.9556f / fConst0);
		float fConst2 = Clave_faustpower2_f(fConst1);
		fConst3 = 2.0f * (1.0f - 1.0f / fConst2);
		float fConst4 = 1.0f / fConst1;
		fConst5 = (fConst4 + -1.4142135f) / fConst1 + 1.0f;
		float fConst6 = (fConst4 + 1.4142135f) / fConst1 + 1.0f;
		fConst7 = 1.0f / fConst6;
		fConst8 = 3.1415927f / fConst0;
		fConst9 = std::max<float>(1.0f, 0.0005f * fConst0);
		fConst10 = 1.0f / fConst9;
		fConst11 = 0.8f / (fConst2 * fConst6);
	}
	
	virtual void instanceResetUserInterface() {
		fHslider0 = FAUSTFLOAT(2.5e+03f);
		fButton0 = FAUSTFLOAT(0.0f);
		fHslider1 = FAUSTFLOAT(0.09f);
		fHslider2 = FAUSTFLOAT(0.7f);
	}
	
	virtual void instanceClear() {
		for (int l0 = 0; l0 < 2; l0 = l0 + 1) {
			fVec0[l0] = 0.0f;
		}
		for (int l1 = 0; l1 < 3; l1 = l1 + 1) {
			fRec1[l1] = 0.0f;
		}
		for (int l2 = 0; l2 < 3; l2 = l2 + 1) {
			fRec0[l2] = 0.0f;
		}
		for (int l3 = 0; l3 < 2; l3 = l3 + 1) {
			iRec2[l3] = 0;
		}
	}
	
	virtual void init(int sample_rate) {
		classInit(sample_rate);
		instanceInit(sample_rate);
	}
	
	virtual void instanceInit(int sample_rate) {
		instanceConstants(sample_rate);
		instanceResetUserInterface();
		instanceClear();
	}
	
	virtual Clave* clone() {
		return new Clave();
	}
	
	virtual int getSampleRate() {
		return fSampleRate;
	}
	
	virtual void buildUserInterface(UI* ui_interface) {
		ui_interface->openVerticalBox("clave");
		ui_interface->addHorizontalSlider("decay", &fHslider1, FAUSTFLOAT(0.09f), FAUSTFLOAT(0.02f), FAUSTFLOAT(0.4f), FAUSTFLOAT(0.001f));
		ui_interface->addHorizontalSlider("freq", &fHslider0, FAUSTFLOAT(2.5e+03f), FAUSTFLOAT(8e+02f), FAUSTFLOAT(4e+03f), FAUSTFLOAT(1.0f));
		ui_interface->addHorizontalSlider("gain", &fHslider2, FAUSTFLOAT(0.7f), FAUSTFLOAT(0.0f), FAUSTFLOAT(1.0f), FAUSTFLOAT(0.01f));
		ui_interface->addButton("gate", &fButton0);
		ui_interface->closeBox();
	}
	
	virtual void compute(int count, FAUSTFLOAT** RESTRICT inputs, FAUSTFLOAT** RESTRICT outputs) {
		FAUSTFLOAT* output0 = outputs[0];
		FAUSTFLOAT* output1 = outputs[1];
		float fSlow0 = std::tan(fConst8 * float(fHslider0));
		float fSlow1 = 2.0f * (1.0f - 1.0f / Clave_faustpower2_f(fSlow0));
		float fSlow2 = 1.0f / fSlow0;
		float fSlow3 = (fSlow2 + -0.016666668f) / fSlow0 + 1.0f;
		float fSlow4 = (fSlow2 + 0.016666668f) / fSlow0 + 1.0f;
		float fSlow5 = 1.0f / fSlow4;
		float fSlow6 = float(fButton0);
		float fSlow7 = 2e+01f / (fSlow0 * fSlow4);
		float fSlow8 = 1.0f / std::max<float>(1.0f, fConst0 * float(fHslider1));
		float fSlow9 = fConst11 * float(fHslider2);
		for (int i0 = 0; i0 < count; i0 = i0 + 1) {
			fVec0[0] = fSlow6;
			float fTemp0 = fSlow6 - fVec0[1];
			fRec1[0] = fTemp0 * float(fTemp0 > 0.0f) - fSlow5 * (fSlow3 * fRec1[2] + fSlow1 * fRec1[1]);
			fRec0[0] = fSlow7 * (fRec1[0] - fRec1[2]) - fConst7 * (fConst5 * fRec0[2] + fConst3 * fRec0[1]);
			iRec2[0] = (iRec2[1] + (iRec2[1] > 0)) * (fSlow6 <= fVec0[1]) + (fSlow6 > fVec0[1]);
			float fTemp1 = float(iRec2[0]);
			float fTemp2 = fSlow9 * std::max<float>(0.0f, std::min<float>(fConst10 * fTemp1, fSlow8 * (fConst9 - fTemp1) + 1.0f)) * (fRec0[0] + fRec0[2] - 2.0f * fRec0[1]);
			output0[i0] = FAUSTFLOAT(fTemp2);
			output1[i0] = FAUSTFLOAT(fTemp2);
			fVec0[1] = fVec0[0];
			fRec1[2] = fRec1[1];
			fRec1[1] = fRec1[0];
			fRec0[2] = fRec0[1];
			fRec0[1] = fRec0[0];
			iRec2[1] = iRec2[0];
		}
	}

};

#endif
